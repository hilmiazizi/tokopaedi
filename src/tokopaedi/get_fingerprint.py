import random
import uuid
import json
import base64

def randomize_fp():
    iphone_models = [
        "iPhone SE", "iPhone 8", "iPhone X", "iPhone 11", "iPhone 12",
        "iPhone 13", "iPhone 14 Pro", "iPhone 15 Pro Max"
    ]
    ios_versions = ["15.7", "16.6", "17.0", "17.5", "18.0", "18.5"]
    screen_resolutions = [
        "1334x750", "1792x828", "2532x1170", "2778x1284", "2556x1179"
    ]
    user_agents = [
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0_1 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A306 Safari/6531.22.7",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_2 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B146 Safari/8536.25",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_2 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A501 Safari/9537.53",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D167 Safari/9537.53",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E277 Safari/602.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/16A366 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1"
    ]

    # Java Island bounds only
    longitudes = (104.5, 114.0)
    latitudes = (-8.8, -5.5)


    ios_version = random.choice(ios_versions)

    fingerprint = {
        "device_manufacturer": "Apple",
        "timezone": "Asia/Jakarta",
        "location_longitude": str(random.uniform(*longitudes)),
        "location_latitude": str(random.uniform(*latitudes)),
        "idfa": str(uuid.uuid4()).upper(),
        "is_emulator": False,
        "unique_id": str(uuid.uuid4()).upper(),
        "access_type": 1,
        "device_system": "iOS",
        "device_model": "iPhone",
        "is_tablet": False,
        "user_agent": random.choice(user_agents),
        "is_jailbroken_rooted": False,
        "screen_resolution": random.choice(screen_resolutions),
        "versionName": f"2.{random.randint(300, 350)}.{random.randint(0, 9)}",
        "current_os": ios_version,
        "language": "id",
        "device_name": random.choice(iphone_models)
    }

    json_str = json.dumps(fingerprint)
    b64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    return b64_str