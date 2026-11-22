#!/usr/bin/env python3
"""Offline Kokoro scene renderer. Requires local packages, model, voice, and G2P data.

Input JSON: {"scenes": [{"id": "intro", "script": "Spoken text."}, ...]}
Example: python render_local_narration.py --input content.json --output media \
  --model-dir models --voice af_heart --speed .93
The output always records auditory review as pending; technical checks cannot certify pleasantness.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

PINNED_ASSETS = {
    'config.json': (2351,'5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f'),
    'kokoro-v1_0.pth': (327212226,'496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4'),
    'af_heart.pt': (523425,'0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff'),
    'af_bella.pt': (523425,'8cb64e02fcc8de0327a8e13817e49c76c945ecf0052ceac97d3081480e8e48d6'),
}


def parse():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--model-dir',type=Path,required=True)
    p.add_argument('--voice',default='af_heart')
    p.add_argument('--speed',type=float,default=.93)
    p.add_argument('--gap',type=float,default=0.0)
    p.add_argument('--samples',action='store_true',help='Render opening scene with af_heart and af_bella')
    return p.parse_args()


def digest(p):
    result=hashlib.sha256()
    with Path(p).open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):result.update(chunk)
    return result.hexdigest()


def verify_model_assets(model_dir,voices):
    """Check exact official assets before importing/loading the speech runtime."""
    if model_dir.is_symlink():raise RuntimeError('Model directory must not be a symlink.')
    if any(voice not in ('af_heart','af_bella') for voice in voices):
        raise ValueError('Only the pinned af_heart and af_bella voices are supported.')
    for name in ['config.json','kokoro-v1_0.pth',*[voice+'.pt' for voice in voices]]:
        path=model_dir/name
        if path.is_symlink() or not path.is_file():raise RuntimeError('Missing or symlinked model asset: '+name)
        size,expected=PINNED_ASSETS[name]
        if path.stat().st_size!=size or digest(path)!=expected:
            raise RuntimeError('Model asset failed pinned size/SHA-256 verification: '+name+'. Restore it with local narration setup; do not bypass verification.')


def require_output_path(path,file=False):
    """Reject existing output redirects; not a sandbox against concurrent writers."""
    path=Path(path).absolute()
    for item in [*reversed(path.parents),path]:
        if item.is_symlink():raise RuntimeError('Refusing a symlink in the narration output path: '+str(item))
    if file and path.exists() and not path.is_file():raise RuntimeError('Narration output must be a regular file: '+str(path))
    return path


def data_tree_digest(folder):
    result=hashlib.sha256();count=0
    for path in sorted(Path(folder).rglob('*')):
        if path.is_symlink():raise RuntimeError('Bundled pronunciation data contains an unexpected symlink.')
        if path.is_file():
            result.update(path.relative_to(folder).as_posix().encode('utf-8')+b'\0')
            result.update(bytes.fromhex(digest(path)));count+=1
    return result.hexdigest(),count


@contextmanager
def bundled_phonemizer():
    """Keep verified bundled data within eSpeak 1.52's short native path limit.

    This is pronunciation processing for the neural model, not a system TTS voice.
    A short-lived data copy avoids eSpeak's compiled-in build path fallback.
    """
    import espeakng_loader
    import misaki.espeak  # Its module initializer selects the bundled library/data.
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    source=Path(espeakng_loader.get_data_path()).resolve()
    if not (source/'phontab').is_file():raise RuntimeError('Bundled pronunciation data is incomplete; rerun local narration setup.')
    fingerprint,count=data_tree_digest(source)
    info={'package':'espeakng-loader','version':importlib.metadata.version('espeakng-loader'),
        'sourceDataPath':str(source),'activeDataPath':str(source),'dataSha256':fingerprint,
        'dataFiles':count,'temporaryDataCopy':False}
    # Upstream 1.52 uses a 160-byte POSIX path buffer. Keep margin on every OS.
    if len(os.fsencode(str(source)))<150:
        EspeakWrapper.set_data_path(str(source))
        yield info
        return
    with tempfile.TemporaryDirectory(prefix='ae-esp-') as folder:
        target=Path(folder).resolve()/'data'
        if len(os.fsencode(str(target)))>=150:
            raise RuntimeError('The native pronunciation engine needs a short temporary path. Set TMPDIR (macOS/Linux) or TEMP (Windows) to a short writable directory, then rerun rendering.')
        shutil.copytree(source,target)
        if data_tree_digest(target)!=(fingerprint,count):raise RuntimeError('Temporary pronunciation data failed byte verification.')
        EspeakWrapper.set_data_path(str(target))
        info.update(activeDataPath=str(target),temporaryDataCopy=True)
        try:yield info
        finally:EspeakWrapper.set_data_path(str(source))


def main():
    args=parse()
    if not .7<=args.speed<=1.3 or not 0<=args.gap<=3:
        raise ValueError('Use speed .7–1.3 and gap 0–3 seconds.')
    args.output=require_output_path(args.output)
    verify_model_assets(args.model_dir,['af_heart','af_bella'] if args.samples else [args.voice])
    if not importlib.util.find_spec('en_core_web_sm'):
        raise RuntimeError('English G2P data en_core_web_sm is missing. Install it separately; this renderer never downloads it.')
    # No provider calls or implicit credentials. Model and language data must be present before rendering.
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    os.environ['TOKENIZERS_PARALLELISM']='false'
    with bundled_phonemizer() as phonemizer_info:
        render(args,phonemizer_info)


def render(args,phonemizer_info):
    import numpy as np
    import soundfile as sf
    import torch
    from kokoro import KPipeline, KModel
    torch.set_num_threads(4);torch.manual_seed(17)
    content=json.loads(args.input.read_text(encoding='utf-8'))
    scenes=content['scenes']
    if not scenes or any(not isinstance(x.get('script'),str) or not x['script'].strip() for x in scenes):
        raise ValueError('Each scene requires a nonempty script.')
    if len({x['id'] for x in scenes})!=len(scenes):raise ValueError('Scene IDs must be unique.')
    jobs=[(scenes[0],voice,f'sample-{voice}.wav') for voice in ['af_heart','af_bella']] if args.samples else [(scene,args.voice,f'scene-{i:02d}.wav') for i,scene in enumerate(scenes,1)]
    reportname='samples.json' if args.samples else 'timings.json'
    for name in [*[job[2] for job in jobs],reportname,*([] if args.samples else ['narration.wav'])]:
        require_output_path(args.output/name,file=True)
    model=KModel(repo_id='hexgrad/Kokoro-82M',config=str(args.model_dir/'config.json'),model=str(args.model_dir/'kokoro-v1_0.pth')).eval()
    pipeline=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',model=model,device='cpu')
    require_output_path(args.output).mkdir(parents=True,exist_ok=True)
    report={'model':'hexgrad/Kokoro-82M','modelVersion':'1.0','modelLicense':'Apache-2.0',
        'modelSource':'https://huggingface.co/hexgrad/Kokoro-82M','modelSha256':digest(args.model_dir/'kokoro-v1_0.pth'),
        'software':{x:importlib.metadata.version(x) for x in ['kokoro','torch','misaki','soundfile']},
        'phonemizer':{k:v for k,v in phonemizer_info.items() if k not in ['sourceDataPath','activeDataPath']},
        'voice':args.voice,'speed':args.speed,'device':'CPU','inferenceMode':'eval','sampleRate':24000,'channels':1,
        'gapSeconds':args.gap,'playback':'perScene' if args.gap==0 else 'combinedWithGaps','inputSha256':digest(args.input),'review':{'auditory':'pending','technical':'pending'},'scenes':[]}
    combined=[];cursor=0
    for idx,(scene,voice,name) in enumerate(jobs):
        parts=list(pipeline(scene['script'],voice=str(args.model_dir/f'{voice}.pt'),speed=args.speed,split_pattern=r'\n+'))
        chunks=[];segments=[];words_timed=[];offset=.18
        for pidx,result in enumerate(parts):
            sound=result.audio.detach().cpu().numpy()
            for token in (result.tokens or []):
                st=getattr(token,'start_ts',None);en=getattr(token,'end_ts',None)
                if st is not None and en is not None:
                    words_timed.append({'text':token.text,'start':round(offset+float(st),4),'end':round(offset+float(en),4)})
            segments.append({'text':result.graphemes,'phonemes':result.phonemes,'start':round(offset,4),'end':round(offset+len(sound)/24000,4)})
            chunks.append(sound);offset+=len(sound)/24000
            if pidx<len(parts)-1:chunks.append(np.zeros(6000,dtype=np.float32));offset+=.25
        if not chunks:raise RuntimeError('No audio generated for '+scene['id'])
        signal=np.concatenate([np.zeros(4320,dtype=np.float32),*chunks,np.zeros(8400,dtype=np.float32)])
        if not np.isfinite(signal).all():raise RuntimeError('Audio contains nonfinite samples.')
        peak=float(np.max(np.abs(signal)))
        gain=min(1,.95/max(peak,1e-9));signal*=gain
        dest=require_output_path(args.output/name,file=True);sf.write(dest,signal,24000,subtype='PCM_16')
        duration=len(signal)/24000
        words=len(re.findall(r"\b[\w’'-]+\b",scene['script']))
        record={'id':scene['id'],'file':'media/'+name,'duration':round(duration,4),'start':round(cursor,4),'end':round(cursor+duration,4),'voice':voice,
            'sha256':digest(dest),'scriptSha256':hashlib.sha256(scene['script'].encode()).hexdigest(),
            'peak':round(float(np.max(np.abs(signal))),6),'rms':round(float(np.sqrt(np.mean(signal**2))),6),
            'gain':gain,'inputWords':words,'wordsPerMinute':round(words/duration*60,2),'segments':segments,'words':words_timed,'wordTimingMethod':'Kokoro predicted phoneme durations; requires playback spot-check'}
        report['scenes'].append(record);combined.append(signal);cursor+=duration
        if idx<len(jobs)-1:combined.append(np.zeros(round(24000*args.gap),dtype=np.float32));cursor+=args.gap
        print(json.dumps({k:record[k] for k in ['id','file','voice','duration','wordsPerMinute']}),flush=True)
    report['totalDuration']=round(cursor,4)
    report['review']['technical']='finite waveform; recorded duration; peak below 0.95; input hashes recorded. Listening still required.'
    if not args.samples:
        sf.write(require_output_path(args.output/'narration.wav',file=True),np.concatenate(combined),24000,subtype='PCM_16')
        report['audio']='media/narration.wav';report['audioSha256']=digest(args.output/'narration.wav')
    require_output_path(args.output/reportname,file=True).write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':main()
