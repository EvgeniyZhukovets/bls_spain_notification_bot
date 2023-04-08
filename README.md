# BLS notification bot

Getting a spot at Spain's visa center in Yerevan is a quest, so I wrote
a bot to notify me about open slots.

Initially I wanted to make it autofill user data & pass the captcha, but
the site works so unreliably, that it turned out to be a waste of time.

## How to deploy it

You might just start selenium locally and use cron for scheduling, but I wanted
to play around with k8s and wrote a small spec.

```shell
cd deploy
cp overlays/local/.env{.template,}
# put your tg creds here, it is gitignored
vim overlays/local/.env
kubectl kustomize overlays/local | kubectl apply -f -
```

## Troubleshooting

Sometimes bls captcha starts to work, it shows up as errors in the script,
in this case increase the interval between runs via `schedule` param.