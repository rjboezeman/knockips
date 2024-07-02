from pyroute2 import IPSet
from pyroute2.netlink.exceptions import NetlinkError

ipset = IPSet()
all_ipset = ipset.list()
print(f" type of all_ipset: {type(all_ipset)}")

ipset_list = [j[1] for i in all_ipset for j in i['attrs'] if j[0] == 'IPSET_ATTR_SETNAME']
# loop through tuple all_ipset and print type for every entry:
# for i in all_ipset:
#     print(f"i: {i}")
#     print(f" type of i: {type(i)}")
#     print(f"i.attrs: {i['attrs']}")
#     for j in i['attrs']:
#         print(f"j: {j}")
#         print(f" type of j: {type(j)}")
#         print(f"j[0]: {j[0]}")
#         print(f" type of j[0]: {type(j[0])}")
#         print(f"j[1]: {j[1]}")
#         print(f" type of j[1]: {type(j[1])}")
#         if j[0] == 'IPSET_ATTR_SETNAME':
#             ipset_list.append(j[1])

for i in all_ipset:
    for j in i['attrs']:
        if j[0] == 'IPSET_ATTR_ADT':
            # print all things recursively:
            print(f"j: {j}")



print("_______________________________________________")
test_ipset = "sshtrusted"
ssht = ipset.list("sshtrusted")
print(f"ipset_list of sshtrusted: {ssht}")

t = (
    {
        "nfgen_family": 2,
        "version": 0,
        "res_id": 0,
        "attrs": [
            ("IPSET_ATTR_PROTOCOL", 7),
            ("IPSET_ATTR_SETNAME", "fooX2189019"),
            ("IPSET_ATTR_TYPENAME", "hash:ip"),
            ("IPSET_ATTR_FAMILY", 2),
            ("IPSET_ATTR_REVISION", 5),
            ("IPSET_ATTR_INDEX", 0, 16384),
            (
                "IPSET_ATTR_DATA",
                {
                    "attrs": [
                        ("IPSET_ATTR_HASHSIZE", 1024, 16384),
                        ("IPSET_ATTR_MAXELEM", 65536, 16384),
                        ("IPSET_ATTR_BUCKETSIZE", 12),
                        ("IPSET_ATTR_INITVAL", 2429868251, 16384),
                        ("IPSET_ATTR_REFERENCES", 0, 16384),
                        ("IPSET_ATTR_MEMSIZE", 200, 16384),
                        ("IPSET_ATTR_ELEMENTS", 0, 16384),
                    ]
                },
                32768,
            ),
            ("IPSET_ATTR_ADT", {"attrs": []}, 32768),
        ],
        "header": {
            "length": 144,
            "type": 1543,
            "flags": 2,
            "sequence_number": 256,
            "pid": 403956,
            "error": None,
            "target": "localhost",
            "stats": 0
        },
    },
    {
        "nfgen_family": 2,
        "version": 0,
        "res_id": 0,
        "attrs": [
            ("IPSET_ATTR_PROTOCOL", 7),
            ("IPSET_ATTR_SETNAME", "sshtrusted"),
            ("IPSET_ATTR_TYPENAME", "hash:ip"),
            ("IPSET_ATTR_FAMILY", 2),
            ("IPSET_ATTR_REVISION", 5),
            ("IPSET_ATTR_INDEX", 1, 16384),
            (
                "IPSET_ATTR_DATA",
                {
                    "attrs": [
                        ("IPSET_ATTR_HASHSIZE", 1024, 16384),
                        ("IPSET_ATTR_MAXELEM", 65536, 16384),
                        ("IPSET_ATTR_BUCKETSIZE", 12),
                        ("IPSET_ATTR_INITVAL", 675660845, 16384),
                        ("IPSET_ATTR_REFERENCES", 1, 16384),
                        ("IPSET_ATTR_MEMSIZE", 280, 16384),
                        ("IPSET_ATTR_ELEMENTS", 2, 16384),
                    ]
                },
                32768,
            ),
            (
                "IPSET_ATTR_ADT",
                {
                    "attrs": [
                        (
                            "IPSET_ATTR_DATA",
                            {
                                "attrs": [
                                    (
                                        "IPSET_ATTR_IP_FROM",
                                        {
                                            "attrs": [
                                                (
                                                    "IPSET_ATTR_IPADDR_IPV4",
                                                    "145.222.94.129",
                                                )
                                            ]
                                        },
                                        32768,
                                    )
                                ]
                            },
                            32768,
                        ),
                        (
                            "IPSET_ATTR_DATA",
                            {
                                "attrs": [
                                    (
                                        "IPSET_ATTR_IP_FROM",
                                        {
                                            "attrs": [
                                                (
                                                    "IPSET_ATTR_IPADDR_IPV4",
                                                    "99.81.92.51",
                                                )
                                            ]
                                        },
                                        32768,
                                    )
                                ]
                            },
                            32768,
                        ),
                    ]
                },
                32768,
            ),
        ],
        "header": {
            "length": 176,
            "type": 1543,
            "flags": 2,
            "sequence_number": 256,
            "pid": 403956,
            "error": None,
            "target": "localhost",
            "stats": 0
        },
    },
    {
        "nfgen_family": 2,
        "version": 0,
        "res_id": 0,
        "attrs": [
            ("IPSET_ATTR_PROTOCOL", 7),
            ("IPSET_ATTR_SETNAME", "fooX2189621"),
            ("IPSET_ATTR_TYPENAME", "hash:ip"),
            ("IPSET_ATTR_FAMILY", 2),
            ("IPSET_ATTR_REVISION", 5),
            ("IPSET_ATTR_INDEX", 2, 16384),
            (
                "IPSET_ATTR_DATA",
                {
                    "attrs": [
                        ("IPSET_ATTR_HASHSIZE", 1024, 16384),
                        ("IPSET_ATTR_MAXELEM", 65536, 16384),
                        ("IPSET_ATTR_BUCKETSIZE", 12),
                        ("IPSET_ATTR_INITVAL", 2051598119, 16384),
                        ("IPSET_ATTR_REFERENCES", 0, 16384),
                        ("IPSET_ATTR_MEMSIZE", 200, 16384),
                        ("IPSET_ATTR_ELEMENTS", 0, 16384),
                    ]
                },
                32768,
            ),
            ("IPSET_ATTR_ADT", {"attrs": []}, 32768),
        ],
        "header": {
            "length": 144,
            "type": 1543,
            "flags": 2,
            "sequence_number": 256,
            "pid": 403956,
            "error": None,
            "target": "localhost",
            "stats": 0
        },
    },
)
