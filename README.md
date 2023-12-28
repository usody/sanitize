# Usody Sanitize

> Under development.

A tool to securely erase disks by performing a certificate-based validation of
the wipe process.

It ensures that the data on the disk is completely and 
irrecoverably erased, protecting sensitive information from being recovered. 
The tool uses industry-standard wiping methods to securely erase the data on 
the disk, making it impossible to recover. The tool also generates a 
certificate of sanitize process that can be used to verify the authenticity of the wipe
process. This tool is perfect for businesses and individuals who need to
securely and permanently remove sensitive data from their disks.

## Dependencies

This tool uses `hdparm` and `smartmontools` for the sanitize process, make sure to have them installed before running
sanitize.

For Debian users, run the following command:

```bash
apt update
apt install python3-pydantic
```

### Erasure tools dependencies

#### NVME disks

On debian we need the dependency `nvme-cli`.

```bash
apt update
apt install nvme-cli
```

`nvme-cli` is a valuable tool to efficiently and securely erase the data while benefiting from the speed and security
features inherent in NVMe technology. This is particularly important in scenarios where data confidentiality,
performance, and compliance are critical concerns.

## Installation

Install the package from the official PyPi repository:

<div class="termy">

```console
$ pip install usody_sanitize

---> 100%
```

</div>

## Usage

Sanitize is written to make it easy to use via terminal or import and integrate with your code.

### Terminal client

Erase a single disk using the default method: 

```bash
sanitize -d /dev/sdc -m BASIC --confirm
```

### Import client

@Todo: Show some examples.