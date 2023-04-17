"""Pre-defined sanitize methods to erase disks securely."""
from usody_sanitize import schemas


BASIC = schemas.ErasureMethod(
    name="Basic Erasure",
    # https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=917935
    standard="",
    description="A single-pass overwrite of the entire drive with"
                " zeros. This method is relatively fast and simple,"
                " but it may not be completely effective in destroying"
                " all traces of the original data.",
    removal_process="Overwriting",
    program="shred",
    verification_enabled=True,
    bad_sectors_enabled=False,
    overwriting_steps=1,
)

BASELINE = schemas.ErasureMethod(
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
    program="badblocks",
    verification_enabled=False,
    bad_sectors_enabled=True,
    overwriting_steps=1,
)

CRYPTOGRAPHIC = schemas.ErasureMethod(
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
    program="hdparm",
    verification_enabled=False,
)

ENHANCED = schemas.ErasureMethod(
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
    program="badblocks",
    verification_enabled=True,
    bad_sectors_enabled=True,
    overwriting_steps=3,
)
