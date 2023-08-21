# Secrets Management
###### Prepared for Internal
###### Prepared by Sanyam
###### Updated on 21 January 2022

__NOTE__: Update on  March 24, 2022: This has been deprecated and not used anymore.

## Historical approach

For managing secrets, everything is placed in a `.env` file at the root of the repo which is never committed into the version control following the [12-factor app](https://12factor.net/) guidelines.

For deployment on different servers, the `.env` file is placed manually on the server with the configs changed according to different environments.

This approach has the following flaws:

- Requires manual intervention for placing the file on the server before deployment.
- No changes are being tracked for the env variables.
- Sharing of secrets among developers is a hassle.
- Restricts automation in case new env variables are needed to be added.

## Solution

We can encrypt the `.env` file and place it under version control. We can provide access to the developers using [age](https://github.com/mozilla/sops#encrypting-using-age) and servers using [AWS KMS](https://github.com/mozilla/sops#kms-aws-profiles).

This provides a way to provide access to decrypting secrets to the chosen identities.

## Mozilla SOPS (Mozilla Secret OPerationS)

This lets us place the `.env` file for all environments inside the `.envs` directory at the root of the repo. All these files are encrypted using AGE (for local development) and KMS (for decrypting on the servers).

All the files are named prefixed with their env as follows:

- `./envs/.dev.enc.env` for `dev` environment.
- `./envs/.qa.enc.env` for `qa` environment.
- `./envs/.stg.enc.env` for `staging` environment.
- `./envs/.prod.enc.env` for `prod` environment.

Make sure that multiple master keys are used for encrypting each file. To make the process seamless, a `.sops.yaml` file is included with dummy keys.

For encryption use the following command:

```bash
sops --encrypt .env > .envs/.dev.enc.env
```

For decryption:

```bash
sops --decrypt .envs/.dev.enc.env > .env
```

Options for the keys can be either provided through `.sops.yaml` file which is recursively searched from the directory where the `sops` command is run from, or can be provided as a command-line option or even through env variables. Please [refer to the official documentation](https://github.com/mozilla/sops/blob/master/README.rst) for more details.

Make sure to use the AGE public keys for all the devs while encrypting the secret along with the KMS key for a particular env.

Alternatively, command line options can be used mentioning the master keys while encrypting like this:

```bash
sops --encrypt --age <age-key> --kms <kms-key-arn> .env > .envs/.dev.enc.env
```

- The [`updatekeys` command](https://github.com/mozilla/sops/blob/master/README.rst#id13) is useful for adding keys that can be used for decryption of a particular file.

Caveats:

- SOPS uses the extension of the file to decrypt it. In case you're using any other extension than `.env`, provide the `--input-type` command line flag
- YAML files with anchors don't have support currently in SOPS.

## Deployment through Github Actions

We have set up `secrets` in Github for all the different environments containing `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `KMS_ARN`, `AWS_REGION`. For diff environments, these secrets are picked up from env variables prefixed with env names.

`DEV_` for dev env, `QA_` for qa env, `STG_` for staging env, `PROD_` for prod env.

So, `DEV_AWS_ACCESS_KEY_ID`, `DEV_AWS_SECRET_ACCESS_KEY`, `DEV_AWS_REGION`, `DEV_KMS_ARN` makes one set of secrets for `dev` env. So on, and so forth for all the other environments.

### Process

Before deployment/configuration either through automated/manual workflows on Github Actions, the AWS credentials are configured with `secrets` for a given environment, and the corresponding encrypted env file is decrypted using SOPS. This file is then `scp` into the corresponding server before running ansible for configuration/deployment.
