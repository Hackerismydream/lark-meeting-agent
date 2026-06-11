# Raw Meeting Data

Raw public datasets are intentionally not committed.

MeetingBank:

```bash
mkdir -p data/raw/meetingbank
curl -L -o data/raw/meetingbank/MeetingBank.zip "https://zenodo.org/records/7989108/files/MeetingBank.zip?download=1"
unzip data/raw/meetingbank/MeetingBank.zip -d data/raw/meetingbank
```

QMSum:

```bash
git clone --depth 1 https://github.com/Yale-LILY/QMSum data/raw/qmsum
```

VCSum:

```bash
git clone --depth 1 https://github.com/hahahawu/VCSum data/raw/vcsum
```

Do not commit downloaded raw data, screenshots, tokens, private Feishu exports, or customer data.
