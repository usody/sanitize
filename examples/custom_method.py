from usody_sanitize import erasure, schemas

my_method = schemas.Method(
    name="ExampleMethod",
    standard="Test",
    verification_enabled=False,
    overwriting_steps=[  # 3 Steps, 2 random and finalize with zeros.
        schemas.Execution(tool="badblocks", type="random"),
        schemas.Execution(tool="badblocks", type="random"),
        schemas.Execution(tool="shred", type="zeros"),
    ],
)


def erase_all_disks():
    erasure.auto_erase_disks(
        method=my_method,
    )


def erase_one_disks():
    erasure.auto_erase_disks(
        method=my_method,
        disks=['/dev/sda']
    )
