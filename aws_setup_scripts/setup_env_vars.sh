echo "\
export PYTHONPATH=/opt/python:\$PYTHONPATH;\
export VRAY_REPO_BUCKET=vray-repo;\
export DATA_BUCKET=fbcloudrender-testdata;\
export DATA_LOCAL=/data_local;\
" > /etc/profile.d/setup_fbcloudrender_env.sh
