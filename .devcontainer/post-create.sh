#!/bin/bash

echo "[post-create] start" >> ~/status



#############
sudo apt install gh -y
sudo apt install -y python3
sudo apt install -y python3-pip
pip install --break-system-packages -r requirements.txt

wget -O argocd https://github.com/argoproj/argo-cd/releases/download/v2.12.2/argocd-linux-amd64
chmod +x argocd
sudo mv argocd /usr/bin

# start cluster install
python3 cluster_installer.py

echo "[post-create] complete" >> ~/status