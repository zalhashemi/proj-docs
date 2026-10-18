import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="ledgerline", description="Ledgerline admin CLI")
    parser.add_argument("command", choices=["seed", "export"])
    args = parser.parse_args()
    print(f"running {args.command}")


if __name__ == "__main__":
    main()
