#!/usr/bin/env python3
"""Inspect or install optional, free local English narration into one chosen project.

check/plan never create files or contact the network. install is the only mutating action.
The installer requires CPython 3.12, uses a private venv, and never calls a model API.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import array
import contextlib
from email.parser import Parser
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import venv
import wave

SCHEMA = 1
OWNER = 'article-explainer-local-narration'
PINS = {
    "addict": "2.4.0",
    "annotated-doc": "0.0.7",
    "annotated-types": "0.8.0",
    "anyio": "4.16.0",
    "attrs": "26.1.0",
    "babel": "2.18.0",
    "blis": "1.3.4",
    "catalogue": "2.0.10",
    "certifi": "2026.11.20",
    "cffi": "2.1.1",
    "charset-normalizer": "3.5.2",
    "click": "8.5.1",
    "cloudpathlib": "0.26.0",
    "cloudpickle": "3.1.3",
    "confection": "1.3.4",
    "csvw": "4.2.0",
    "curated-tokenizers": "0.0.10",
    "curated-transformers": "0.1.1",
    "cymem": "2.0.16",
    "dlinfo": "2.0.0",
    "docopt": "0.6.2",
    "espeakng-loader": "0.2.4",
    "filelock": "4.3.0",
    "fsspec": "2026.9.0",
    "h11": "0.16.0",
    "hf-xet": "1.8.0",
    "httpcore": "1.0.9",
    "httpcore2": "2.16.2",
    "httpx": "0.28.1",
    "httpx2": "2.16.2",
    "huggingface-hub": "2.4.0",
    "idna": "3.20",
    "isodate": "0.7.2",
    "jinja2": "3.1.6",
    "joblib": "1.6.0",
    "jsonschema": "4.26.0",
    "jsonschema-specifications": "2025.9.1",
    "kokoro": "0.9.4",
    "language-tags": "1.3.2",
    "loguru": "0.8.0",
    "markdown-it-py": "4.3.0",
    "markupsafe": "3.0.4",
    "mdurl": "0.1.2",
    "misaki": "0.9.4",
    "mpmath": "1.3.0",
    "murmurhash": "1.0.16",
    "networkx": "3.7",
    "num2words": "0.5.14",
    "numpy": "2.5.5",
    "packaging": "26.3",
    "phonemizer-fork": "3.3.2",
    "preshed": "3.0.15",
    "pycparser": "3.12",
    "pydantic": "2.14.4",
    "pydantic-core": "2.50.5",
    "pygments": "2.21.0",
    "pyparsing": "3.3.3",
    "python-dateutil": "4.0.0",
    "pyyaml": "6.0.4",
    "rdflib": "7.6.0",
    "referencing": "0.37.0",
    "regex": "2026.11.19",
    "requests": "2.34.2",
    "rfc3986": "1.5.0",
    "rich": "15.0.0",
    "rpds-py": "2026.9.1",
    "safetensors": "0.8.0",
    "segments": "2.4.0",
    "setuptools": "84.2.1",
    "shellingham": "1.5.4",
    "smart-open": "10.0.0",
    "soundfile": "0.14.0",
    "spacy": "3.8.18",
    "spacy-curated-transformers": "0.3.1",
    "spacy-legacy": "3.0.12",
    "spacy-loggers": "1.0.5",
    "srsly": "2.5.6",
    "sympy": "1.14.0",
    "termcolor": "3.3.0",
    "thinc": "8.3.14",
    "tokenizers": "0.23.3",
    "tqdm": "4.70.1",
    "transformers": "5.24.0",
    "truststore": "0.10.5",
    "typer": "0.29.2",
    "typing-extensions": "4.16.0",
    "typing-inspection": "0.4.5",
    "tzdata": "2026.6",
    "uritemplate": "4.2.0",
    "urllib3": "2.8.0",
    "wasabi": "1.1.3",
    "weasel": "1.0.1",
    "wrapt": "2.5.2"
}
ASSETS = [
 {'name':'config.json','url':'https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/config.json','size':2351,'sha256':'5abb01e2403b072bf03d04fde160443e209d7a0dad49a423be15196b9b43c17f'},
 {'name':'kokoro-v1_0.pth','url':'https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v1_0.pth','size':327212226,'sha256':'496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4'},
 {'name':'af_heart.pt','url':'https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_heart.pt','size':523425,'sha256':'0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff'},
 {'name':'af_bella.pt','url':'https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_bella.pt','size':523425,'sha256':'8cb64e02fcc8de0327a8e13817e49c76c945ecf0052ceac97d3081480e8e48d6'},
 {'name':'en_core_web_sm-3.8.0-py3-none-any.whl','url':'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl','size':12806118,'sha256':'1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85'},
]
SMOKE = {'scenes':[{'id':'setup-check','script':'A local narrator turns this short passage into speech. Listen for clear words, comfortable pacing, and a natural voice before using it for a longer explanation.'}]}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def read_json(path):
    try:
        result=json.loads(Path(path).read_text(encoding='utf-8'))
        return result if isinstance(result,dict) else None
    except (OSError,ValueError):return None


def atomic_json(path,data):
    path=Path(path);tmp=path.with_name(path.name+'.tmp')
    if path.is_symlink() or tmp.is_symlink():raise RuntimeError('Refusing a symlink at '+str(path))
    tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,path)


def profile_info():
    system=platform.system();arch=platform.machine().lower();why=[]
    result={'system':system,'architecture':arch,'python':platform.python_version(),'supported':False,
            'evidence':'No executed test for this platform profile.','torchVersion':None}
    if platform.python_implementation()!='CPython' or sys.version_info[:2]!=(3,12):
        why.append('Run this installer with CPython 3.12. See first-run.md for a private Python installation.')
    if system=='Darwin' and arch in ('arm64','aarch64'):
        major=int(platform.mac_ver()[0].split('.')[0] or 0)
        if major<14:why.append('These pinned Torch/NumPy wheels require macOS 14 or newer.')
        result.update(profile='macos-arm64',torchVersion='2.15.0',evidence='Runtime tested on Apple Silicon macOS; fresh installer validation is separate. OS minimum comes from wheel tags.')
    elif system=='Windows' and arch in ('amd64','x86_64'):
        if sys.getwindowsversion().major<10:why.append('The Windows route requires Windows 10 or newer.')
        result.update(profile='windows-x64',torchVersion='2.15.0+cpu',evidence='Official CPython 3.12 CPU/native wheels verified; not executed on Windows. The smoke test must pass locally.')
    elif system=='Linux' and arch in ('amd64','x86_64'):
        libc,version=platform.libc_ver()
        try:compatible=libc=='glibc' and tuple(int(x) for x in version.split('.')[:2])>=(2,28)
        except ValueError:compatible=False
        if not compatible:why.append('The CPU Torch wheel needs glibc 2.28+. Alpine/musl is not covered; use a compatible glibc distribution or a separately verified runtime profile.')
        result.update(profile='linux-x64',torchVersion='2.15.0+cpu',evidence='Official CPython 3.12 CPU/native wheels verified; not executed on Linux. The smoke test must pass locally.')
    else:
        why.append('No pinned runtime profile for this OS/architecture. Inspect official PyTorch CPU wheels and package compatibility, then validate an isolated profile; do not substitute a paid API or a robotic voice.')
        if system=='Darwin':why.append('Recent PyTorch releases do not provide this profile for Intel Macs; an older compatible CPU stack needs separate validation.')
    result['supported']=not why;result['issues']=why
    return result


def python_at(state):return state/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')


def child_env(state):
    env={k:v for k,v in os.environ.items() if not k.startswith('PIP_') and k not in {
        'PYTHONPATH','PYTHONHOME','VIRTUAL_ENV','OPENAI_API_KEY','ANTHROPIC_API_KEY','HF_TOKEN','HUGGING_FACE_HUB_TOKEN'}}
    env.update(PIP_CONFIG_FILE=os.devnull,PIP_DISABLE_PIP_VERSION_CHECK='1',PIP_NO_INPUT='1',
        PIP_CACHE_DIR=str(state/'cache/pip'),HF_HOME=str(state/'cache/huggingface'),XDG_CACHE_HOME=str(state/'cache'),
        HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
    return env


def require_managed_path(state,path):
    """Reject symlinks inside the managed boundary before reading or writing."""
    state=Path(state);path=Path(path)
    relative=path.relative_to(state)
    for item in [state.parent,state,*[state.joinpath(*relative.parts[:i]) for i in range(1,len(relative.parts)+1)]]:
        if item.is_symlink():raise RuntimeError('Refusing a symlink inside the managed narration directory: '+str(item))
    return path


def versions(state):
    """Read package declarations as data; never launch the project's interpreter."""
    result={}
    site=state/'.venv'/('Lib/site-packages' if os.name=='nt' else 'lib/python3.12/site-packages')
    try:
        require_managed_path(state,site)
        for directory in sorted(site.glob('*.dist-info')):
            metadata=require_managed_path(state,directory/'METADATA')
            if not metadata.is_file() or metadata.stat().st_size>1024*1024:continue
            headers=Parser().parsestr(metadata.read_text(encoding='utf-8'),headersonly=True)
            name=re.sub(r'[-_.]+','-',headers.get('Name','')).lower()
            version=headers.get('Version','')
            if not name or not re.fullmatch(r'[a-z0-9][a-z0-9-]*',name) or not version:continue
            result[name]='ambiguous duplicate metadata' if name in result else version
        return result
    except (OSError,ValueError,RuntimeError):return {}


def expected_versions(profile):return {**PINS,'torch':profile.get('torchVersion'),'en-core-web-sm':'3.8.0'}


def file_ok(path,asset):
    return path.is_file() and not path.is_symlink() and path.stat().st_size==asset['size'] and sha(path)==asset['sha256']


def inspect_state(project,profile):
    state=project/'.article-explainer/narration';renderer=Path(__file__).resolve().with_name('render_local_narration.py')
    try:marker=read_json(require_managed_path(state,state/'managed.json'))
    except RuntimeError:marker=None
    owned=marker is not None and marker.get('owner')==OWNER and marker.get('schema')==SCHEMA
    installed=versions(state) if owned else {}
    dependency_issues=[f'{k}: expected {v}; found {installed.get(k,"missing")}' for k,v in expected_versions(profile).items() if installed.get(k)!=v]
    assets=[]
    for asset in ASSETS:
        try:verified=file_ok(require_managed_path(state,state/'models'/asset['name']),asset)
        except RuntimeError:verified=False
        assets.append({'name':asset['name'],'verified':verified})
    try:smoke=read_json(require_managed_path(state,state/'smoke/verification.json')) or {}
    except RuntimeError:smoke={}
    smoke_wav=state/'smoke/media/narration.wav'
    try:
        require_managed_path(state,smoke_wav)
        smoke_valid=bool(smoke.get('passed') and renderer.is_file() and smoke.get('rendererSha256')==sha(renderer)
            and smoke_wav.is_file() and smoke.get('audioSha256')==sha(smoke_wav))
    except RuntimeError:smoke_valid=False
    ready=profile['supported'] and owned and not dependency_issues and all(x['verified'] for x in assets) and smoke_valid
    return {'projectDirectory':str(project),'stateDirectory':str(state),'interpreter':str(python_at(state)),
        'profile':profile,'managedDirectory':owned,'dependencies':dependency_issues,'assets':assets,
        'smokeVerified':smoke_valid,'ready':ready,
        'inspection':'Static package declarations and recorded smoke evidence only; no project code was executed. This does not establish trust in an existing runtime.',
        'auditoryQuality':'A generated smoke sample needs actual listening; setup success does not certify a pleasing narrator.'}


def print_plan(project,profile):
    print(json.dumps({'action':'plan','writesFiles':False,'usesNetwork':False,'projectDirectory':str(project),
        'stateDirectory':str(project/'.article-explainer/narration'),'profile':profile,
        'dependencies':expected_versions(profile),'sources':['https://download.pytorch.org/whl/cpu','https://pypi.org/simple',*[a['url'] for a in ASSETS]],
        'minimumFreeDiskBytes':3*1024**3,'assetDownloadBytes':sum(a['size'] for a in ASSETS),
        'additionalDependencyDownloads':'Platform-dependent, commonly hundreds of MB; CPU wheels only. No API/credit costs.',
        'steps':['Create a private venv under the chosen project','Install pinned CPU Torch from the official CPU index','Install remaining pinned dependencies from PyPI','Download and SHA-256-verify public model, voices, and English language data','Run pip check, import verification, and an actual offline synthesis smoke test','Record versions, sources, hashes, and smoke evidence']},indent=2))


@contextlib.contextmanager
def install_lock(state):
    lock=state/'install.lock'
    if lock.is_symlink():raise RuntimeError('Refusing symlink lock file.')
    with lock.open('a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        try:
            if os.name=='nt':
                import msvcrt
                f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:raise RuntimeError('Another setup process is using this project. Wait for it to finish.')
        try:yield
        finally:
            if os.name=='nt':
                f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(f.fileno(),fcntl.LOCK_UN)


def run_logged(args,state,name):
    if Path(name).name!=name:raise RuntimeError('Log name must be a single filename.')
    log=require_managed_path(state,state/'logs'/name)
    fd,temporary=tempfile.mkstemp(prefix='.setup-log-',dir=log.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,env=child_env(state))
        require_managed_path(state,log)
        os.replace(temporary,log)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)
    if r.returncode:raise RuntimeError('Command failed; review '+str(log)+'. Fix the reported cause, then rerun install; completed downloads are retained.')


def require_runtime_trust(state,trust_existing_runtime):
    folder=require_managed_path(state,state/'.venv')
    if folder.is_dir() and any(folder.iterdir()) and not trust_existing_runtime:
        raise RuntimeError('An existing runtime contains executable project code, including possible Python startup hooks. Reuse requires --trust-existing-runtime for a project you created or independently verified. A managed.json marker or package metadata does not establish trust. For copied or untrusted state, choose a fresh project directory.')


def verify_runtime_launcher(state):
    """Check structure and selected base without executing project code.

    This detects a replaced launcher; it does not authenticate installed packages.
    Reusing their executable code separately requires explicit runtime trust.
    """
    py=python_at(state)
    require_managed_path(state,py.parent)
    cfg=require_managed_path(state,state/'.venv/pyvenv.cfg')
    if not py.is_file() or not cfg.is_file():raise RuntimeError('The existing runtime is incomplete. Use a fresh project directory for a clean setup.')
    values={}
    for line in cfg.read_text(encoding='utf-8').splitlines():
        key,separator,value=line.partition('=')
        if separator:values[key.strip().lower()]=value.strip()
    base=Path(getattr(sys,'_base_executable',sys.executable)).resolve()
    if values.get('include-system-site-packages','').lower()!='false' or values.get('version')!=platform.python_version():
        raise RuntimeError('Existing runtime configuration differs from the selected isolated Python. Run setup with its original base interpreter or use a fresh project directory.')
    if Path(values.get('home','')).resolve()!=base.parent or (values.get('executable') and Path(values['executable']).resolve()!=base):
        raise RuntimeError('Existing runtime points to a different base interpreter. Use its original trusted interpreter or a fresh project directory.')
    candidates=[base]
    if os.name=='nt':
        candidates += [Path(venv.__file__).parent/'scripts/nt/python.exe',base.parent/'venvlauncher.exe']
    if not any(candidate.is_file() and sha(py)==sha(candidate) for candidate in candidates):
        raise RuntimeError('Existing runtime launcher does not match the selected trusted Python. It was not executed; choose a fresh project directory.')
    require_managed_path(state,state/'.venv'/('Lib/site-packages' if os.name=='nt' else 'lib/python3.12/site-packages'))
    return py


def ensure_environment(state,trust_existing_runtime=False):
    require_runtime_trust(state,trust_existing_runtime)
    py=python_at(state)
    folder=state/'.venv'
    if not folder.exists() or not any(folder.iterdir()):
        print('Creating or completing the isolated Python environment.',flush=True)
        venv.EnvBuilder(with_pip=True,clear=False,system_site_packages=False).create(state/'.venv')
    py=verify_runtime_launcher(state)
    # -S suppresses .pth/sitecustomize during this structural probe. Later pip and
    # renderer execution intentionally use the explicitly trusted environment.
    probe=subprocess.run([str(py),'-I','-S','-B','-c','import sys,json; print(json.dumps({"version":list(sys.version_info[:2])}))'],capture_output=True,text=True,env=child_env(state))
    try:details=json.loads(probe.stdout)
    except ValueError:raise RuntimeError('The managed Python cannot start. Choose a fresh project directory with a working CPython 3.12 interpreter.')
    if probe.returncode or details['version']!=[3,12]:
        raise RuntimeError('The existing runtime is not the expected isolated Python 3.12 environment. Choose a fresh project directory; no global packages were changed.')
    pip_probe=subprocess.run([str(py),'-I','-B','-m','pip','--version'],capture_output=True,text=True,env=child_env(state))
    if pip_probe.returncode:
        print('Restoring pip from this Python installation’s bundled ensurepip.',flush=True)
        run_logged([str(py),'-I','-B','-m','ensurepip','--upgrade'],state,'ensurepip-repair.log')
    return py


def safe_download_reason(exc):
    if isinstance(exc,urllib.error.HTTPError):
        if exc.code==404:return 'HTTP 404: the pinned official asset is unavailable. Verify the packaged release URL before retrying; do not use an unofficial mirror.'
        if exc.code in (401,403):return 'HTTP '+str(exc.code)+': public asset access was denied. Check network access to the official host; do not add API credentials.'
        if exc.code==429:return 'HTTP 429: the official host rate-limited this download. Wait and rerun install to resume.'
        return 'HTTP '+str(exc.code)+': the official host could not complete the download. Rerun later to resume.'
    reason=getattr(exc,'reason',exc)
    if isinstance(reason,(ssl.SSLCertVerificationError,ssl.SSLError)):
        return 'TLS certificate verification failed. Repair the trusted certificate chain or supply an approved --ca-bundle; never disable TLS verification.'
    if isinstance(exc,RuntimeError):
        return str(exc)+' Verify the official release and pinned checksum; never disable checksum verification.'
    if isinstance(reason,TimeoutError):return 'Network timeout. Rerun install; completed and partial downloads are retained.'
    if isinstance(exc,urllib.error.URLError):return 'The official download host could not be reached. Check network/proxy access and rerun install to resume.'
    return type(exc).__name__+': local transfer or filesystem failure. Check available disk space, write access, and network connectivity; rerun to resume.'


def tls_context(py,state,ca_bundle=None):
    ctx=ssl.create_default_context()
    if ca_bundle:ctx.load_verify_locations(cafile=str(ca_bundle))
    # ensurepip supplies pip's CA bundle in a fresh venv, avoiding an undeclared global certifi dependency.
    r=subprocess.run([str(py),'-I','-B','-c','from pip._vendor import certifi; print(certifi.where())'],capture_output=True,text=True,env=child_env(state),check=True)
    ctx.load_verify_locations(cafile=r.stdout.strip())
    return ctx


def download(asset,folder,context):
    target=folder/asset['name'];partial=target.with_name(target.name+'.part')
    if target.is_symlink() or partial.is_symlink():raise RuntimeError('Refusing symlink asset path.')
    if file_ok(target,asset):return 'reused'
    for attempt in range(3):
        try:
            offset=partial.stat().st_size if partial.exists() else 0
            if offset==asset['size'] and sha(partial)==asset['sha256']:
                os.replace(partial,target);return 'resumed'
            if offset>=asset['size']:partial.unlink();offset=0
            headers={'User-Agent':'article-explainer-local-setup/1','Accept-Encoding':'identity'}
            if offset:headers['Range']=f'bytes={offset}-'
            req=urllib.request.Request(asset['url'],headers=headers)
            with urllib.request.urlopen(req,context=context,timeout=60) as response:
                if response.status==206:
                    cr=response.headers.get('Content-Range','')
                    match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',cr)
                    if not match or int(match[1])!=offset or int(match[3])!=asset['size']:
                        raise RuntimeError('Server returned an inconsistent byte range.')
                elif response.status==200:offset=0
                else:raise RuntimeError('Unexpected download status '+str(response.status))
                with partial.open('ab' if offset else 'wb') as out:
                    total=offset
                    while True:
                        chunk=response.read(1024*1024)
                        if not chunk:break
                        total+=len(chunk)
                        if total>asset['size']:raise RuntimeError('Download exceeded expected size.')
                        out.write(chunk)
            if not file_ok(partial,asset):
                if partial.stat().st_size==asset['size']:partial.unlink()
                raise RuntimeError('Downloaded bytes did not match the pinned size/checksum.')
            os.replace(partial,target);return 'downloaded'
        except (OSError,urllib.error.URLError,http.client.HTTPException,RuntimeError) as exc:
            if attempt==2:
                detail=safe_download_reason(exc)
                raise RuntimeError(f'Could not verify {asset["name"]} after three attempts. {detail}') from None
            time.sleep(attempt+1)
    raise RuntimeError('Download failed.')


def smoke_test(state,renderer):
    folder=state/'smoke';folder.mkdir(exist_ok=True);atomic_json(folder/'input.json',SMOKE)
    py=python_at(state)
    run_logged([str(py),'-I','-B',str(renderer),'--input',str(folder/'input.json'),'--output',str(folder/'media'),
        '--model-dir',str(state/'models'),'--voice','af_heart','--speed','.93','--gap','0'],state,'smoke.log')
    audio=folder/'media/narration.wav';metadata=read_json(folder/'media/timings.json')
    with wave.open(str(audio),'rb') as w:
        if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,2,24000):raise RuntimeError('Smoke audio format is incorrect.')
        frames=w.getnframes();samples=array.array('h',w.readframes(frames))
    if sys.byteorder!='little':samples.byteswap()
    duration=frames/24000;peak=max(abs(x) for x in samples)/32768 if samples else 0
    rms=(sum((x/32768)**2 for x in samples)/len(samples))**.5 if samples else 0
    if not 2<duration<40 or not .001<peak<=.951 or rms<.0001:raise RuntimeError('Smoke audio is empty, silent, clipped, or has an implausible duration.')
    scene=metadata['scenes'][0]
    if abs(metadata['totalDuration']-duration)>1/24000 or scene['sha256']!=sha(folder/'media/scene-01.wav'):
        raise RuntimeError('Smoke timing/hash validation failed.')
    words=scene.get('words',[])
    if not words or not all(0<=x['start']<=x['end']<=duration for x in words):raise RuntimeError('Smoke word cues are invalid.')
    proof={'passed':True,'durationSeconds':duration,'peak':peak,'rms':rms,'audioSha256':sha(audio),
        'rendererSha256':sha(renderer),'wordCues':len(words),'auditoryReview':'pending actual listening'}
    atomic_json(folder/'verification.json',proof)
    return proof


def install(project,profile,ca_bundle=None,trust_existing_runtime=False):
    if not profile['supported']:raise RuntimeError(' '.join(profile['issues']))
    state=project/'.article-explainer/narration';renderer=Path(__file__).resolve().with_name('render_local_narration.py')
    if not renderer.is_file():raise RuntimeError('Packaged renderer is missing; restore the complete skill directory.')
    ancestor=project
    while not ancestor.exists():ancestor=ancestor.parent
    if shutil.disk_usage(ancestor).free<3*1024**3:raise RuntimeError('Keep at least 3 GiB free for the isolated runtime, model, and temporary downloads.')
    if state.is_symlink() or (project/'.article-explainer').is_symlink():raise RuntimeError('Refusing a symlink setup directory.')
    marker=read_json(require_managed_path(state,state/'managed.json'))
    if state.exists() and any(state.iterdir()) and (not marker or marker.get('owner')!=OWNER or marker.get('schema')!=SCHEMA):
        raise RuntimeError('The setup directory contains unrecognized files. Choose another project directory; existing files were not changed.')
    require_runtime_trust(state,trust_existing_runtime)
    for name in ['models','cache','logs','smoke']:
        folder=require_managed_path(state,state/name)
        if folder.is_dir():
            for item in folder.rglob('*'):require_managed_path(state,item)
    state.mkdir(parents=True,exist_ok=True);atomic_json(state/'managed.json',{'owner':OWNER,'schema':SCHEMA})
    with install_lock(state):
        for name in ['models','cache','logs','smoke','.venv']:
            if (state/name).is_symlink():raise RuntimeError('Refusing symlink managed directory: '+name)
            if name!='.venv':(state/name).mkdir(exist_ok=True)
        py=ensure_environment(state,trust_existing_runtime)
        installed=versions(state);expected=expected_versions(profile)
        changed=False
        pip=[str(py),'-I','-B','-m','pip','--disable-pip-version-check','--no-input','--cache-dir',str(state/'cache/pip')]
        if ca_bundle:pip+=['--cert',str(ca_bundle)]
        if installed.get('torch')!=expected['torch']:
            print('Installing pinned CPU Torch from the official PyTorch index.',flush=True)
            run_logged(pip+['install','--no-deps','--only-binary=:all:','--index-url','https://download.pytorch.org/whl/cpu','torch=='+expected['torch']],state,'torch-install.log');changed=True
        if any(installed.get(k)!=v for k,v in PINS.items()) or changed:
            print('Installing pinned speech dependencies from PyPI.',flush=True)
            run_logged(pip+['install','--only-binary=:all:','--no-binary=docopt','--index-url','https://pypi.org/simple',*[f'{k}=={v}' for k,v in {**PINS,'torch':expected['torch']}.items()]],state,'dependencies-install.log');changed=True
        context=tls_context(py,state,ca_bundle)
        asset_actions={}
        for asset in ASSETS:
            print('Verifying '+asset['name']+'.',flush=True)
            asset_actions[asset['name']]=download(asset,state/'models',context)
            changed=changed or asset_actions[asset['name']]!='reused'
        if installed.get('en-core-web-sm')!='3.8.0':
            run_logged(pip+['install','--no-deps',str(state/'models'/ASSETS[-1]['name'])],state,'language-install.log');changed=True
        print('Checking dependencies and rendering an offline speech sample.',flush=True)
        run_logged(pip+['check'],state,'pip-check.log')
        status=inspect_state(project,profile)
        if status['dependencies']:raise RuntimeError('Installed package versions differ from the tested profile: '+str(status['dependencies']))
        if changed or not status['smokeVerified']:proof=smoke_test(state,renderer)
        else:proof=read_json(state/'smoke/verification.json')
        installed=versions(state)
        provenance={'schema':SCHEMA,'owner':OWNER,'checkedAtUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'profile':profile,'pythonExecutable':str(py),'packages':installed,'sources':{'torch':'https://download.pytorch.org/whl/cpu','dependencies':'https://pypi.org/simple'},
            'assets':ASSETS,'assetActions':asset_actions,'rendererSha256':sha(renderer),'smoke':proof,
            'paidAPICalls':False,'apiCreditsUsed':False,'globalEnvironmentModified':False}
        atomic_json(state/'provenance.json',provenance)
        print(json.dumps(inspect_state(project,profile),indent=2))
        print('Setup passed. Listen to '+str(state/'smoke/media/narration.wav')+' before accepting voice quality.',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['check','plan','install'])
    p.add_argument('--project-dir',type=Path,required=True)
    p.add_argument('--ca-bundle',type=Path,help='Optional trusted CA bundle for an organization-managed network. TLS verification stays enabled.')
    p.add_argument('--trust-existing-runtime',action='store_true',help='Allow install to execute an existing project runtime you created or independently verified. Never infer trust from managed.json or copied package metadata. Not needed for a fresh empty runtime.')
    args=p.parse_args();project=args.project_dir.expanduser().resolve();profile=profile_info()
    if args.action=='check':
        result=inspect_state(project,profile);print(json.dumps(result,indent=2));return 0 if result['ready'] else 2
    if args.action=='plan':print_plan(project,profile);return 0
    try:install(project,profile,args.ca_bundle,args.trust_existing_runtime)
    except (OSError,RuntimeError,subprocess.SubprocessError) as exc:
        print('Setup incomplete: '+str(exc),file=sys.stderr);return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
