# Phase 1 Component SHA-256 Manifest

Date: 2026-08-12

Hashes are lowercase SHA-256. “Parent” means the exact official upstream release asset; “slim” means the repository's deterministic kext-only or selected-member archive. Executable hashes are over the principal Mach-O bytes extracted from the archive.

## Official parent assets

| Component / variant | Exact local source | SHA-256 | Acquisition |
|---|---|---|---|
| OpenCore 1.0.7 RELEASE | `/Users/kgp/Developer/OCLP-Plus-Mod-evaluation-audit/RELEASE_ASSETS/Acidanthera/OpenCore-1.0.7-RELEASE.zip` | `2ffab6ebf58c7aefb0bcb3a1a385d207746823d6dd87d44bd666e1286939943e` | reused |
| OpenCore 1.0.7 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/OpenCore-1.0.7-DEBUG.zip` | `3644db831dd18344896d7a86077b8c338c0eaa01b1579d7fa00785598cac1f2b` | official download; no existing copy found |
| Lilu 1.7.2 RELEASE | completed audit `RELEASE_ASSETS/Acidanthera` | `53967d7dcfaab01023a33df2e969a89522f13d6654a6a56ac4711b62dabf3ab8` | reused |
| Lilu 1.7.2 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/Lilu-1.7.2-DEBUG.zip` | `e95df95d82e8b151047abf359ecd9c853755c59293e19dfcc3907da8fbd8cf89` | official download |
| WhateverGreen 1.7.0 RELEASE | completed audit `RELEASE_ASSETS/Acidanthera` | `6d6ffe8334ad60f784a662794e67b2560b79d757d506841dc8ca9994ab39979b` | reused |
| WhateverGreen 1.7.0 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/WhateverGreen-1.7.0-DEBUG.zip` | `3900aba46c38a42593977fec8ad5bd0f5cd00934a0c2074272e9a623a46c4483` | official download |
| RestrictEvents 1.1.6 RELEASE | completed audit `RELEASE_ASSETS/Acidanthera` | `98170dfae195ddd28b5d95e3f040125a13ca783bcb9bd1e5b8c588e217b14ee6` | reused |
| RestrictEvents 1.1.6 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/RestrictEvents-1.1.6-DEBUG.zip` | `6ff7b0a28dbee66429fb50c588f50e43f0c231245182a4f7a7542e934956ec86` | official download |
| AirportBrcmFixup 2.2.0 RELEASE | completed audit `RELEASE_ASSETS/Acidanthera` | `4543a097c120e19f848a8f60e0dbb2d42359f368feb3c217d725b6fe8cd384e1` | reused |
| AirportBrcmFixup 2.2.0 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/AirportBrcmFixup-2.2.0-DEBUG.zip` | `32b313b2202f5c7b9b358cb0e97ec2515240315f4f1cbc5d570298a1626a8686` | official download |
| BrcmPatchRAM 2.7.2 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `e1c1c55347526d031a8ae2fdd1f52efa3019161e497fb38e1cfa809752f8af21` | reused |
| BrcmPatchRAM 2.7.2 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/BrcmPatchRAM-2.7.2-DEBUG.zip` | `268d1a9f32ca80db398b6d415242b01d8f70a5ccc861c6f86069c450abca5ac4` | official download |
| NVMeFix 1.1.3 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `e1d5657ab7ac31f69771708f7b80bf218ab9aa0b8e4c4fe6ff943983037e3dfb` | reused |
| NVMeFix 1.1.3 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/NVMeFix-1.1.3-DEBUG.zip` | `14bddc4d7336f5a781dd3201afd174ebe117b584e62f98e6f2acad50c8b5ffda` | official download |
| CPUFriend 1.3.0 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `37645d960f0b3c958cfd0a8a041160532267ec535c4979897123df89c7dbdcde` | reused |
| CPUFriend 1.3.0 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/CPUFriend-1.3.0-DEBUG.zip` | `0b11b6edee735a7b1f83e1a945ec2b684eb1d2ef56420c3d9f96ea38c2fcff91` | official download |
| CryptexFixup 1.0.5 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `25041d94a0fe9a0261caf0ba89b36dfcb21682bf3c697a34bcaddc839576ab30` | reused |
| CryptexFixup 1.0.5 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/CryptexFixup-1.0.5-DEBUG.zip` | `8e528e8ae6d2585688b28de301b183c1391fbe8f7bfd9c603dfa5f5e6cc5658a` | official download |
| DebugEnhancer 1.1.1 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `2c0978c43fb6179fd5195ddec14c4dd9ab2eb46262021a33fcab78b5568ef67f` | reused |
| DebugEnhancer 1.1.1 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/DebugEnhancer-1.1.1-DEBUG.zip` | `533a023a3b50f77ca4b0b4c5a24cdd48dad8aebc0ce4e93eead88e8232fd6f1e` | official download |
| FeatureUnlock 1.1.8 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `b1b85c31fe48fc899ac838b013c9b64a842f6f33265200b5ace3ecec5caa045c` | reused |
| FeatureUnlock 1.1.8 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/FeatureUnlock-1.1.8-DEBUG.zip` | `6be8a2a014eab25fd5032017c8c08910f34ee38590a7c91d40f0fa05c65c6721` | official download |
| AppleALC 1.9.7 RELEASE | completed audit `WORK/COMPONENT_MODERNIZATION/OFFICIAL` | `81a8ba79986130e8c845fff595950226cbc30e588f8d37089e467f776469c29d` | reused |
| AppleALC 1.9.7 DEBUG | `WORK/PHASE1_OFFICIAL_ASSETS/AppleALC-1.9.7-DEBUG.zip` | `6769c7c833e3692cf5d08c4d472d59f80dfbdb8646754a8a685be8e33164b78b` | official download after exhaustive local search |

## Kext payloads: before and after

Each cell is `slim archive / principal executable`.

| Component / variant | Before | After |
|---|---|---|
| Lilu DEBUG | `65939039ffe87f7dd5b0cc49b6d6774ad658eea7280a65875d8e9985e53804d5` / `28c43ac78e5bb36aa9532c93ea7f0f4efd0fe3b392d18a8a66b1f256e6f5a31e` | `96d5d4e24ac00622c0301063de6a7451e680b241a785775c41e40e33881f7f40` / `438b912da9057fadfab8c366ad7ac2eada5227f415622ec7fc5037c06e2cffa5` |
| Lilu RELEASE | `8031fffbf0349f0f65e1af60cb193e30bd5b7a8385f3c2f8bd040d6459933c15` / `d42a643ed5fd951535e9580cd27ac6c47ceb6534c447f1937e8d3868846b7738` | `c747220827cada058569def08e48892f6019b33455803c721eef1461035da4dc` / `ff98508b40a1eb5fb477029db8886412520f8e39965279ea331c99e3d2e3b274` |
| WhateverGreen DEBUG | `740c14b225427417e38fa10fcfd85fa3fd114696ec67ad6ac029bc726f47586a` / `bb3f62b4dd4e823479ad1ed066e7c38bbc4abeb9a06cfc8d2e4eb0b3c27bfb40` | `028f27985ad44d992bd650718a01680d70ed54d0e45d189c6909de765323c10b` / `76e8a60e9ea155b841b9740e8ea3b17bdec5d6ff6dbac33a594c379ae6c612f6` |
| WhateverGreen RELEASE | `ba75d38ff0d23844a7ac8ebf139c1a090afe537da2a7bf15ad92a2f962277213` / `342b9216dc8cf37c17c0ccdd1f117e186f7ae3e519eaad2e1f8fc5c8d94f989e` | `2a9ba08ca08217398f764db64db9f93df205c393205d0d5c8c4246d14f90bc1c` / `44b6273a8dcf4d89fa454c402f1626f57ec9a7efb3e3a2d4bd70eaef2c508562` |
| RestrictEvents DEBUG | `517f6db64326c6446c26c00eb2abdb8c1a4921883e097397296b2b00adb811d4` / `e21ba26189e08d64e9a07dd24b94644def9c1a76db7e69846ea4b34e766a38f8` | `effdb06a12fa91821897569d21b0a9606a0fffb2dbafbf8d5694d5fe610f3851` / `6613749e0f8c7b03b9fa6deaaf951c635fd601ad0b656938ded0374bc60a7b48` |
| RestrictEvents RELEASE | `facfeca41913938c451dcd7d567e6dfd353c8318a5e09f8575206b8ddb37d438` / `789c6a814cb92c80e39a3c018289727cec6732b3ff01a21c97ad679cce786ddc` | `f6668ddae218ae01726cef325e2cb88f05ba5e8aa00717cf95938e5199d63c45` / `16979236f272c0500913882e5347e38d5bad1841ea619fe5a0311e9f768aea4e` |
| AirportBrcmFixup DEBUG | `d838dd830e319b16931894d0b3e7650635ca7308dfc74257f8711ceddb8d85ec` / `bce3caf858b531173449a7981703f3bfc15944cf8e8b9e0dc61ef6e1b712f708` | `9116889049aeb46f1b501c261ef75d89e19bd6d51a20add97980148d455744cc` / `ac0b53bb1cee5f69a1276b20dd65c5ec80cd53fa301db47aa446c0db97a8e5b1` |
| AirportBrcmFixup RELEASE | `9a5acabb9ac57c9af89ee4157d1fa40812920db048b2e1dcfbdf5bdd65c3db74` / `40c3c05e45449e2fb4883ddd4a65aec2bb77ca8f2c7b03bb2487867f23246365` | `e4884c930ab0c8bceb1f8955a214c65a24b5a2ba267686c93cd16532427ad030` / `e1705483bb03deda6ef34a5db5b3597149674de5a947c28a7d71fb693c963fe0` |
| BlueToolFixup DEBUG | `db2e93e54a382f34669cb698e18605aefec15e9ed7f6abb5de005606b18e7cdd` / `16e601078e70aa729badb3188ccaad404339ebc257c55f94133f9c1aa142dc45` | `cc181d142e7cd9e4b266c5876f77aaf570c56a2738e295d29f81a6275c318d20` / `b4e0eec2161397f2446285c2baad483cdad9b818eb1e1189f85eeb302a2a1bd3` |
| BlueToolFixup RELEASE | `34a75e51e8030126181a1dc6c13a327d2f7c294bed6423fde2e6ddd3e8f355f9` / `cd60f99e3587817a05ca3f132c9e0716b8197965e68d2bb15579acf8169f9618` | `357d0eedef093bb3c69c38e4466c632f7669cd1daf00de3f52a8a5d6f14ae133` / `f3244382a43866138ff449b14f1e54fb069ad3e4b14cbc753858650efdbbce52` |
| NVMeFix DEBUG | `5ba128b5d34a6bad5aaff18f002829a89d8d53850c9c5286a683026e5c650ddd` / `9c98fb6060e4cba798102928d8b1952160c04b973f4f1227906f3824d77fd88b` | `589edef198d8447d412b7234d78e8440c0a56324628b74e68c0622f8dd807245` / `8d44110df6b287d4df54c68937b140cf27d46ce8feb029aff46efce211dd5839` |
| NVMeFix RELEASE | `4a1ba112e326989da1d7e65b45b51ad2586101590f914a680749bf84453b5ee5` / `1ef89859c5e1a2251b0afa7dc40b4d1931e89e7b7caf78226d3228da8215bfb8` | `8ff0f0b084af7ab468626b6ef4c9c87bb81ec83a0c7cecc349c7284514cb717c` / `3e2632eaf09c6cb87e88c5681371e194c53b6653ddbf8693f0bbb1ae42470ef8` |
| CPUFriend DEBUG | `a0d94af89a55b2f022371a0a62b6a7cb3f7ed1b527fd801cef0a5e981643228e` / `55b1d04ce76e555f016d8fd29b0ca6a516d69e62671e15cfe6bc6c9c8dd25c72` | `7f32868248854c3154457f7aff121dc4f145cd89731f00e15d66a6137c8afac1` / `be62a2532f370222df032aeab6c30e8e3a5c944c33067bd8a7a5454a25ccc41c` |
| CPUFriend RELEASE | `556b83d36d96755dc34368a5dcd1bef87e6dd3c5a999d4254c5e6db6212f5f35` / `3df9d19fc4c67ddebbce530a9ed3352fdf898ad35b152b9283a3a7d1adec4cef` | `1842c8ae2484b6519543a78d8672430eb6695caf42524e3552bcb525f82d0e47` / `36c3897684642942bd0dc60f20ecdf002aa375ce1788fa0cefc5e7282418dd76` |
| CryptexFixup DEBUG | `ef3623b4c7e23e0b29d4905cd09a6eb860842aac79ea4083d74f09f47d54a2aa` / `7bb62a1b016c360f2505bd623210967ca587ffb28f3aba23599155c623b35f63` | `a470e8301514231d0c6301adbf683cd1689a2a9b2d0ea6660a836007b002c130` / `5465e61cb5e75f6e6280686f86f7c4a54d9408075b2b862f9141b21316c2822f` |
| CryptexFixup RELEASE | `160685757088e331fcb5ee43eb07e74b1e40a68b80903992a8cf79b59375b210` / `baaef65579a7bf734c19f06d4030dced9577a611a67c588818981aac1c35fae3` | `5fc8c974ed91aa52f51525c6aef8df036599280563f1d69580c98f1d9a90a170` / `7d746c6a07f3afdd53235d7a7d5bb3a1f2ed94e8dd99eeeabb0e54c04e8444f7` |
| DebugEnhancer DEBUG | `af7af29f97cd4b32000871581b457f4345437c29e6d12b2bcde65faa6be47908` / `fb23c1f07306e337cbdff7ee15e1d5d48b98d45480dffd906678e0df9721ab1b` | `7b1a54f933fa1c107d0854d78f271f1385add2d88d67194b00332cd746ffa914` / `a7cb89e0f0dd6de3dae33022fc950b6270dbb3d2dc0d06af4b6cb008a117c760` |
| DebugEnhancer RELEASE | `d2d5a83474e5785106c5cabdee12237faa1bbe87653d9c039aacd6fa343a85e8` / `a104984b9f7c5e5721cc96779970d522093a043e6e59fc1d78b6d7d419527b7f` | `4cf8fed66a3bf20d90459534a082d76d06b553cecbbb220a41d596f5b30a618f` / `22ee3825ec574833f53cd673326b826c0ceec7d4ae74a48892b6512dd58f1f21` |
| FeatureUnlock DEBUG | `a776659326cb55c90de7ec3e1c0014959b3a2c02ac975b1bb52a11dc3963a332` / `2d206cdc909219d536a970aae8a1e8c7ee0f3de4d1c10c6721df83fc000a8ee2` | `c563405cc7643db29c405f53891b7f3161651f7be5acf44f26945d792b273d70` / `853d190e50280cfc176fcf0186e2f26e01ccb184f9ac8cc388bca34e8c8082cf` |
| FeatureUnlock RELEASE | `2ac150ecaaa92a3cce471b94b6548190e4d1984d78db83fa0c87949cc7e7fd39` / `3ec48f1937fb6a7b26a25068dac4e5c8d760cf986ee91e03fbec433e09564c31` | `18febf9e758c42e4764da3a684222218d010d10d7da201040ded158512f61c6d` / `af99c5612e81ec01d185689a163afd0caf72cf6d67d1b6756eadf3d345490bd2` |
| AppleALC DEBUG | `167c896d26f29fe67e84675193579f63c817cc00b4a5d87504bb81fed813961c` / `04a4e35a1ae4d21bec15c0565536245d35dc3a7d37231bf25f650f5f7e990a86` | `f84864d80c5dcb5a0321ec97fd7ff9fadf8945baaff33fb971cd86fb41f25a59` / `38a57eda103d7aaf4bf27b64f61e3e972388bf7517ae8da013d86d6512ec1434` |
| AppleALC RELEASE | `f0179f00351fcd630164478673cbccb84098122a47cea9afe1e2ecfbc56924ed` / `2dd9eb5d040ff0a552baa9ef2a5b17c7357bb437a30297ce84f503d0012b79c2` | `79680e6dba45c6866d6b32c8821fad584542e4414122cc440a48bfe561aaad4a` / `5b67211797985272949b352eff0bb797504903a2ea4598e2d75d0ceca0ed5aa4` |

## OpenCore suite and standalone identities

| Item | Before | After |
|---|---|---|
| OpenCore DEBUG slim archive | `91df2ba0eb6cb3c4838fd05dfdecd42843dae0f3f9e3d18f78829480871ec911` | `e1a9a959c85ea1c7a72e2772a582b728902c52e5dc985e379bf6953552d8e7df` |
| OpenCore RELEASE slim archive | `7552975604213b41f96a8bf29eb6d3a42d8fcdfbfe0ff4d8e163639c7ef65f93` | `d22c3a6850e007edd5f52edfed064bb6c0c3d34c592af8d7fb80222068f94472` |
| macserial | `7cca1169dd6f4daf029795f4ca3d33db06755e348fb83dde4555c87435a74f74` | `c920802bbba68bdcf3da7e1db3c45a1e0756b5a653c869db9ff8142272c57231` |
| ocvalidate | `dfb6f8389686993a87495af3b2c453e6b51fa257ace7ba6befdaa32ed4a3eb23` | `bcaf32c0615cd17e31f8e61be4e0485e9bd0e6a9196433f4c1596380af0dc18f` |
| NvmExpressDxe | `a5af3aa9e6eca8b4179a4ed255679269e58ca65d1aa9b65b0afc23e0771246fb` | `7b560cf9d1682761419669a5dcd4c0a1e674546be9ae2016335d9146b825796b` |
| XhciDxe | `dc0b1df416eb82aefd397da56bf353a11fa5c4d3cb737c0f44c6a82641bad178` | `315a295b3e992ae22223dca16783daa425e12ede77d0449e3f98851282e88d3f` |

Official 1.0.7 inner-member SHA-256:

| Member | DEBUG | RELEASE |
|---|---|---|
| `System/Library/CoreServices/boot.efi` | `d56d0d9c70f0cf36352185691583e833f53708e37636f4ff84f11c2cb443b241` | `59b63de9f95d82e50103450391568ef93e0dbf205ebd57f298df237e8e579dcc` |
| `EFI/OC/OpenCore.efi` | `5b8f26ae9485bb43422d651a4e3633e1add5b2553282939011963668fb1eef34` | `8e83a37b8885b8f91aad1232a8a7491848102f85b7339563c5fd4b30af27d2b8` |
| `OpenShell.efi` | `704cf4e8e8440f1f69581421c45c3b488f3a15093430486513f7feaf81e70c5e` | `d33e07731e714f18343766167fc34957268db96d6cdac303ac27c68971428f27` |
| `BootKicker.efi` | `45da31d1bbb449421977cc13e3ba61a90d8bfe6441b76d780c9a7974585966d0` | `d82f25f61b2976338604ee3251b0fd1c19a189525c9563c89e10ba5937afe49c` |
| `OpenRuntime.efi` | `515691e43b735a1bc6b29215baf8d0b411f2bda4bb78223ccaaeb03a9eaf8f44` | `c88586da7145354a0338719b34aabdbbb5c0908a519145c46c6022d6b2fa0b2d` |
| `ResetNvramEntry.efi` | `5baf26935fc5e64e16622812b46e662a5de033901505752a149230239e110bed` | `e826c6b5813aa87e61b799fc7250a09b231629699abffb6ad7a3f2eb7c3a31a9` |
| `OpenCanopy.efi` | `419663f03d569314824648519b5cb2e4a82e22db035871206641713439ba43ba` | `8000524fd157664b0bd4c6c11a9ca7e8df7df2daf738854d781cf5da6d9dfe41` |
| `OpenLinuxBoot.efi` | `b235fdc7df922cb3ad6dafc1d62857ed8cab2afbc02818a5d73c9391d449b953` | `6a17636e97902cf3c5c6d17f0e43751349f2e0505746405765f3f5351492d027` |
| `OpenLegacyBoot.efi` (packaged, builder removes) | `2d0f93bb9a85d88aecebfab839d87838d8528ba6d46b714b61f102a48a78b6e4` | `874ac75dfa50c85a2c66fd39068fd6d1d4de3be80843c916ae7e6d5e558706d7` |

## Frozen boundary identities

| Item | SHA-256 |
|---|---|
| AMFIPass 1.4.1 archive | `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e` |
| AMFIPass principal executable | `4c35bc196d35c69b5f9dca83fe733801211c7828716f51585c7f5450039ca884` |
| PatcherSupportPkg `Universal-Binaries.dmg` | `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` |
| IO80211FamilyLegacy archive | `e681dcc76a2cd2cea4b0ad5f27a3c816055fde3cdccd890dd10a3e2c84e96d93` |
| IOSkywalkFamily archive | `1e12b7ef42f55b39ea54ada97b46331220668b2c48a28656e9875c5145fe2479` |
| Beta-1 AppleHDA executable | `6bf19c385a1212160be8a01fd7903aaa0416407e0b52e949f49d04cee4c65de7` |
| Beta-1 AppleHDA `__text` | `135b98fbccd0c8cd742b50f01a563054eef506f81bcc7799b5fb6429df063096` |
| local Navi WhateverGreen 1.6.9-Navi RELEASE archive | `c7c841f1776f40009eeb0a1d23c697a49fb76be772ee14863d30abad78a91474` |

## Root-patch source identities

| File | SHA-256 before and after |
|---|---|
| `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py` | `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97` |
| `opencore_legacy_patcher/sys_patch/patchsets/hardware/misc/modern_audio.py` | `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d` |

## Final policy and unchanged-boundary source identities

| File | Final SHA-256 | Status |
|---|---|---|
| `opencore_legacy_patcher/constants.py` | `e6921a80ab0ce7841b0223d072e730989f3b17b2a248e73301063d8d8c27a8ad` | approved component version declarations |
| `opencore_legacy_patcher/efi_builder/build.py` | `65380814d0c6f5fff52377a0c81a3eab9f257016868214dc93e491a263b51098` | final centralized boot-argument policy |
| `opencore_legacy_patcher/efi_builder/graphics_audio.py` | `dc6b28da0b793db286dc5907897f4a3a33fdfe562d5232c7407b8b5c3463cea6` | AppleALC gate unchanged; obsolete beta-argument block removed |
| `opencore_legacy_patcher/efi_builder/security.py` | `c0929ea54c0890ec74923d54b8b5a26ecabf0c176b6cbcf9681c762042134336` | byte-identical to baseline; AMFIPass enabler unchanged |
| `opencore_legacy_patcher/efi_builder/networking/wireless.py` | `1551de078fe38633f555702c6055ffe01719e4ba98ad4881dc5ad1b7ce2b46d7` | byte-identical to baseline |
