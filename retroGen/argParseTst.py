import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='add Sprint retro pages to Kepler')
    parser.add_argument('sprint', type=int,
                        help='Sprint Number')
    parser.add_argument('user', type=str, help='Kepler username')
    parser.add_argument('password', type=str, help='Kepler password')

    args = parser.parse_args()
    print(args.user)
    print(args.password)
    print(args.sprint)
