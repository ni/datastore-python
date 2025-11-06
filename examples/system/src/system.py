"""How to detect, publish, and query system hardware and software resources."""

import nisyscfg


def main() -> None:
    """Detect, publish, and query hardware and software resources from the local system."""
    hardware, software = detect_system_resources()


def detect_system_resources(
    system_target: str = "localhost",
) -> tuple[dict[str, object], dict[str, object]]:
    """Return available hardware and software resources on the system_target."""
    hardware = {}
    software = {}

    with nisyscfg.Session(target=system_target) as session:
        filter = session.create_filter()
        filter.is_present = True
        filter.is_ni_product = True
        filter.is_device = True

        hardware = {entry.name: entry for entry in session.find_hardware(filter)}
        software = {entry.id: entry for entry in session.get_installed_software_components()}

    return hardware, software


if __name__ == "__main__":
    main()
