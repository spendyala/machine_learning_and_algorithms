# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from jupyter_core.paths import jupyter_data_dir
import subprocess
import os
import errno
import stat
from subprocess import check_call

# detect if this is container is running on a mac
# this is a bit hacky and if docker changes significantly, it won't work, and it may have some false
# positives as well, but for now, it works
on_mac = 'linuxkit' in os.uname().release

c = get_config()
# in latest version of docker, the docker host IP is being written as the last line in /etc/hosts
# specifying this will avoid a warning
for line in open('/etc/hosts', 'r'):pass
c.NotebookApp.ip = f'{line.split()[0]}'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.token = ''

try:
    from credstash import get_session_params, listSecrets, getSecret
    session_params = get_session_params('ds-notebook', None)
    items = [item['name'] for item in listSecrets(**session_params) if item['name'] in [
        'notebook.password', 'notebook.token', 'github.client_id', 'github.client_secret', 'google.drive.client_id'
    ]]
except Exception:
    items = []

if on_mac:
    # if we are running on a mac, then go ahead and don't require authentication, we are
    # in all probibility running on a developers laptop...
    c.NotebookApp.password = ''
    c.NotebookApp.token = ''
else:
    if 'notebook.password' in items:
        c.NotebookApp.password = f"{getSecret('notebook.password', **session_params)}"
    if 'notebook.token' in items:
        c.NotebookApp.token = f"{getSecret('notebook.token', **session_params)}"
if 'github.client_id' in items:
    c.GitHubConfig.client_id = f"{getSecret('github.client_id', **session_params)}"
if 'github.client_secret' in items:
    c.GitHubConfig.client_secret = f"{getSecret('github.client_secret', **session_params)}"

# Generate a self-signed certificate
if 'GEN_CERT' in os.environ:
    dir_name = jupyter_data_dir()
    pem_file = os.path.join(dir_name, 'notebook.pem')
    try:
        os.makedirs(dir_name)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(dir_name):
            pass
        else:
            raise
    # Generate a certificate if one doesn't exist on disk
    subprocess.check_call(['openssl', 'req', '-new',
                           '-newkey', 'rsa:2048',
                           '-days', '365',
                           '-nodes', '-x509',
                           '-subj', '/C=XX/ST=XX/L=XX/O=generated/CN=generated',
                           '-keyout', pem_file,
                           '-out', pem_file])
    # Restrict access to the file
    os.chmod(pem_file, stat.S_IRUSR | stat.S_IWUSR)
    c.NotebookApp.certfile = pem_file


# Autosave .html and .py versions of the notebook for easier diffing with version control systems
def post_save(model, os_path, contents_manager):
    """post-save hook for converting notebooks to .py scripts"""
    if model['type'] != 'notebook':
        return  # only do this for notebooks
    d, fname = os.path.split(os_path)
    output_dir = os.path.join(d, '.diffs')
    check_call(['jupyter', 'nbconvert', '--to', 'script', '--output-dir', output_dir, fname], cwd=d)
    check_call(['jupyter', 'nbconvert', '--to', 'html', '--output-dir', output_dir, fname], cwd=d)

if 'DOCKER_DS_DIFFS' in os.environ and os.environ['DOCKER_DS_DIFFS'] == '1':
    c.FileContentsManager.post_save_hook = post_save