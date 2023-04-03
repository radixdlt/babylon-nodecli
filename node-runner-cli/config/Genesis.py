import os.path


class GenesisConfig:

    @staticmethod
    def create_nebunet_genesis_file(genesis_json_location: str):
        nebunet_genesis: str = "03999923a98c80255d3b338210739e702f5c379823431712a19d041bbd4c69ab090295fb7f79e3e38b278a39b8cdb1af415f44f0affefeff35f01f2487b25e29a08f034786c902fea0a26e70841b081bffdee4f91eb9ea38ade8cb5ae519987c98b302033a907465ef283d4295a09151ae803200d3ef93b0e0a24cec87d2a7c169ced46c"
        GenesisConfig.create_genesis_file(genesis_json_location, nebunet_genesis)

    @staticmethod
    def create_gilganet_genesis_file(genesis_json_location: str):
        gilganet_genesis: str = "02dc7b732cce3750b38a170b6ecd410a5bbeb429e04b7627d6a242b0e4c92d587a03a37fe25a2af3c65f1b015be13389d870b9f4f9ae0444b151eb46483122ef64420284610c6a7b8c0ffaead58ac921fd5d6a08de3177d64ac21f341a4c254175b61b02e51d5b2e8bb48ca1e7bf104e01fd8184c0520bf2e5e0e8400a99ca9a9cc79027"
        GenesisConfig.create_genesis_file(genesis_json_location, gilganet_genesis)

    @staticmethod
    def create_kisharnet_genesis_file(genesis_json_location: str):
        kisharnet_genesis: str = "02d86679542c9ffa9d04c31e268b3abe69ac5206ab257fcb1e94116377bb9a636c033776fc2ce449b8e8b9bcb1b9ef9ddf8acbc1f1431f303afc865db64e5f4aef19024543f76bc28c790a31e0932293733ad4bbdf9d58d6576bd7ca9c53293acb335402ba61f8c3af1688f7d7341666a64df71a0308346813a6210f6bec3d906c13bdea"
        GenesisConfig.create_genesis_file(genesis_json_location, kisharnet_genesis)


    @staticmethod
    def create_genesis_file(genesis_json_location: str, genesis: str):
        if not os.path.exists(genesis_json_location):
            f = open(genesis_json_location, "w")
            filecontent = f"{{\"genesis\": \"{genesis}\"}}"
            f.write(filecontent)
            f.close()
