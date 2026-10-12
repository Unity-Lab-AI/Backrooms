# Published Linux-amd64 base, not our final custom image digest.
FROM --platform=linux/amd64 python@sha256:b4d66d07136c546f1765eae2bfcce9a64fa95f37c717c02bedd06d0476d1dbbd
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
COPY DEBIAN_SNAPSHOT.json /opt/unity-build/DEBIAN_SNAPSHOT.json
RUN python -c "import hashlib,json,urllib.request; s=json.load(open('/opt/unity-build/DEBIAN_SNAPSHOT.json')); [(lambda r,w: (_ for _ in ()).throw(ValueError('APT snapshot differs')) if hashlib.sha256(r).hexdigest()!=w else None)(urllib.request.urlopen(i['url'],timeout=45).read(),i['sha256']) for i in s['indexes']]" \
    && rm -f /etc/apt/sources.list.d/debian.sources \
    && printf '%s\n' 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20261010T000000Z/ bookworm main' 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian-security/20261010T000000Z/ bookworm-security main' > /etc/apt/sources.list \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends build-essential openssh-server util-linux ca-certificates espeak-ng libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-build.lock.txt requirements-runtime.lock.txt /opt/unity-build/
RUN python -m pip install --no-deps --require-hashes -r /opt/unity-build/requirements-build.lock.txt \
    && python -m pip install --no-deps --no-build-isolation --require-hashes -r /opt/unity-build/requirements-runtime.lock.txt \
    && python -m pip check
ADD --checksum=sha256:51c6f5a7e6f6c7cd4a52373f2262b9aeb0f16084e39595d25f71bc0cf5bc826b https://github.com/runpod/runpodctl/releases/download/v2.15.0/runpodctl-linux-amd64 /usr/local/bin/runpodctl
RUN chmod 755 /usr/local/bin/runpodctl \
    && printf '%s\n' 'PasswordAuthentication no' 'PermitRootLogin prohibit-password' > /etc/ssh/sshd_config.d/unity.conf
COPY export_environment.py start_no_training.sh environment.lock.json /opt/unity-build/
RUN chmod 755 /opt/unity-build/start_no_training.sh \
    && python /opt/unity-build/export_environment.py /opt/unity-environment
EXPOSE 22
# Initial future launch is key-only SSH. Training is a separate action.
ENTRYPOINT ["/opt/unity-build/start_no_training.sh"]
