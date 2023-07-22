"""Pre-defined sanitize methods to erase disks securely."""
from usody_sanitize import schemas


BASIC = schemas.Method(
    name="Basic Erasure",
    # https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=917935
    standard="",
    description="A single-pass overwrite of the entire drive with"
                " zeros. This method is relatively fast and simple,"
                " but it may not be completely effective in destroying"
                " all traces of the original data.",
    removal_process="Overwriting",
    verification_enabled=True,
    bad_sectors_enabled=False,
    overwriting_steps=[
        schemas.Execution(tool="shred", pattern="random"),
    ],
)

BASELINE = schemas.Method(
    name="Baseline Erasure",
    standard="NIST, Infosec HGM Baseline",
    description="Method for securely erasing data in compliance"
                " with HMG Infosec Standard 5 guidelines includes"
                " a single step of a random write process on the"
                " full disk. This process overwrites all data with"
                " a randomized pattern, ensuring that it cannot be"
                " recovered. Built-in validation confirms that the"
                " data has been written correctly, and a final"
                " validation confirms that all data has been deleted.",
    removal_process="Overwriting",
    verification_enabled=False,
    bad_sectors_enabled=True,
    overwriting_steps=[
        schemas.Execution(tool="badblocks", pattern="random"),
    ],
)

CRYPTOGRAPHIC_ATA = schemas.Method(
    name="Baseline Cryptographic",
    standard="NIST, Infosec HGM Baseline",
    description="Method for securely erasing data in compliance"
                " with HMG Infosec Standard 5 guidelines includes"
                " a single step of a random write process on the"
                " full disk. This process overwrites all data with"
                " a randomized pattern, ensuring that it cannot be"
                " recovered. Built-in validation confirms that the"
                " data has been written correctly, and a final"
                " validation confirms that all data has been deleted.",
    removal_process="Overwriting",
    verification_enabled=False,
    overwriting_steps=[
        schemas.Execution(tool="hdparm"),
    ],
)

CRYPTOGRAPHIC_NVME = schemas.Method(
    name="Baseline Cryptographic",
    standard="NIST, Infosec HGM Baseline",
    description="Method for securely erasing data in compliance"
                " with HMG Infosec Standard 5 guidelines includes"
                " a single step of a random write process on the"
                " full disk. This process overwrites all data with"
                " a randomized pattern, ensuring that it cannot be"
                " recovered. Built-in validation confirms that the"
                " data has been written correctly, and a final"
                " validation confirms that all data has been deleted.",
    removal_process="Overwriting",
    verification_enabled=False,
    overwriting_steps=[
        schemas.Execution(tool="nvme"),
    ],
)

ENHANCED = schemas.Method(
    name="Enhanced Erasure",
    standard="HMG Infosec Standard 5",
    description="Method for securely erasing data in compliance"
                " with HMG Infosec Standard 5 guidelines includes"
                " a single step of a random write process on the"
                " full disk. This process overwrites all data with"
                " a randomized pattern, ensuring that it cannot be"
                " recovered. Built-in validation confirms that the"
                " data has been written correctly, and a final"
                " validation confirms that all data has been deleted.",
    removal_process="Overwriting",
    verification_enabled=True,
    bad_sectors_enabled=True,
    overwriting_steps=[
        schemas.Execution(tool="badblocks", pattern="random"),
        schemas.Execution(tool="badblocks", pattern="random"),
        schemas.Execution(tool="shred", pattern="zeros"),
    ],
)
