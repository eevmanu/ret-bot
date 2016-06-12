from fim import fpgrowth


def get_association_rules(transactions):
    result = fpgrowth(transactions, target='r', conf=80, eval='c', report='hbalc')
    result = sorted(result, key=lambda x: (-x[-1], -x[-2]))[:10]
    return [(x[1], x[0]) for x in result]


def get_recommended_product(transactions):
    return get_association_rules(transactions)[0][1]

if __name__ == '__main__':
    with open('parsed.txt') as f:
        tracts = [[i for i in x.split()] for x in f.read().splitlines()]
    print get_recommended_product(tracts)
