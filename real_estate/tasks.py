from celery import shared_task
from .models import HouseImage, Favorite, UserLocation, Searchable, UserProfile, Prompt, House, Synonyms
from .serializers import HouseSerializer
from django.core.mail import send_mail
from .utils.maps import calculate_distance, get_coordinates_from_address, calculate_geodesic_distance
import environ
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from .utils.gemeni import *
from rest_framework import status
from rest_framework.response import Response
import requests
from django.db import connection
from fake_useragent import UserAgent
from urllib.parse import parse_qs
import random
from django.contrib.auth.models import AnonymousUser
import urllib


@shared_task
def replace_house_image_urls():
    images = HouseImage.objects.filter(replaced=False)
    for image in images:
        image.image = str(image.image).replace('http://', 'https://')
        image.replaced = True
        image.save()

    return f"Processed {images.count()} images."


@shared_task
def check_and_notify_users():
    users = User.objects.all()
    factory = RequestFactory()
    for user in users:
        user_prompt = UserProfile.objects.filter(user=user).first()
        if user_prompt:
            prompt_search(user_prompt.prompt, user)
            check_and_notify_user(user.id)


@shared_task
def check_and_notify_user(user_id):
    env = environ.Env()
    environ.Env.read_env()
    user_location = UserLocation.objects.filter(user_id=user_id).first()
    if not user_location:
        return "User location not found."
    favorites = Favorite.objects.filter(user_id=user_id).select_related('house')
    searchables = Searchable.objects.filter(user_id=user_id).select_related('house')
    houses = favorites.union(searchables)
    print(houses)
    for favorite in houses:
        house = favorite.house
        latitude, longitude = get_coordinates_from_address(f"{house.address}, {house.city}")
        if latitude is None or longitude is None:
            continue
        # house_location = f"{latitude},{longitude}"
        # user_location_str = f"{user_location.latitude},{user_location.longitude}"

        distance = calculate_geodesic_distance(latitude, longitude, user_location.latitude, user_location.longitude)
        # distance = calculate_distance(user_location_str, house_location)
        if distance <= float(env("ZONE_DISTANCE")):
            send_mail(
                'House 9odamek',
                f'Your favorite house {house.title} is within the zone.',
                env("EMAIL_HOST"),
                ["yassine.ghizi2@gmail.com"],
                # [user_location.user.email],
                fail_silently=False,
            )


@shared_task
def prompt_search(prompt, user):
    env = environ.Env()
    environ.Env.read_env()
    url = f"{env('GEMENI_ENDPOINT')}{str(random.randint(1000000000000000000, 9999999999999999999))}&hl=fr&_reqid={str(random.randint(1000000, 9999999))}&rt=c"
    headers = {
        "Referer": env("GEMENI_REFERER"),
    }
    print("---------------------------------------")
    print(prompt)
    print("---------------------------------------")
    prompt_template = Prompt.objects.all().order_by("order").first()
    final_prompt = prompt_template.text.replace('{text_to_replace}', f'\"{prompt}\"')
    table_name = House._meta.db_table
    final_prompt = final_prompt.replace('{house_table_name}', f'\'{table_name}\'')
    cookie_1psidts, cookie_3psidts, cookie_1psidcc, cookie_3psidcc = get_cookie()
    ua = UserAgent()
    headers['User-Agent'] = ua.random
    headers["Cookie"] = f"SEARCH_SAMESITE=CgQIy5oB; _ga=GA1.1.1838195142.1710699097; SID=g.a000iAi0d1i_cMN21fdk7sY4S2mVLmaQY0VXieP0h1t2wfhFcG77cUQ1bhmOXUwMe-xKBtr_KgACgYKAV8SAQASFQHGX2Miiu2LQkYPsqOINi7WoBCesBoVAUF8yKoqaBkOSYgwHaF6HK_RRBgU0076; __Secure-1PSID=g.a000iAi0d1i_cMN21fdk7sY4S2mVLmaQY0VXieP0h1t2wfhFcG77vLxDiYTkY4qe-eUn5BcAngACgYKAfISAQASFQHGX2MiTbw9JwUXnA_m1ULGWsYH6BoVAUF8yKoaY_68XimZsYLaSTcAyDge0076; __Secure-3PSID=g.a000iAi0d1i_cMN21fdk7sY4S2mVLmaQY0VXieP0h1t2wfhFcG77D3BeFFH50o6FGeewaGUIcAACgYKAZcSAQASFQHGX2Mi1Lm5RQsl2vInR0K5cr8p5BoVAUF8yKqngQd151GsBYdhO_OxwCcf0076; HSID=AEZXNCdS_Itjp5bvs; SSID=AEX_l_ULObAreQ-uw; APISID=LtrqXbEs68KtIV7W/AmywXc6U1QbT1BA91; SAPISID=dRmITJ9HBc4KTksn/Ae515bnoKS9D6aBUf; __Secure-1PAPISID=dRmITJ9HBc4KTksn/Ae515bnoKS9D6aBUf; __Secure-3PAPISID=dRmITJ9HBc4KTksn/Ae515bnoKS9D6aBUf; __Secure-ENID=18.SE=U-lSXl_MW7cg8_DUJ_dPODNG3QaPB1ztC40plGwJq7kn3Z3qkT3YiHmByTqiPsQUzx93LVWu67FCWFHK1ueYIuY7Bi9ksZpsaaOAZ6wK3wn-yTFJTHTxB9ICbBDSzD35MdEWs-ZWsV0vCag_f_b9qzPXhZWR0lUz4Ac9HUPn_CB_iFkdKoeM58U4217VBgcUKtUtuVhBvjbsIpC4eqH4ytUHZJY_ljyMAYy9dghyLLs2mrE-uZHP7IC3-rwgDEzdcVWxHzlZgPE0448qTzpNowZr6CCZP8N77BYt4l6jbQ; AEC=AQTF6HxzLVTZWsN5rAIL5dc5jHT1GDSebgCFj1wGQa3uZQVNxBIci4GIwJ8; NID=513=HyI7OE2N4NoBnG2KYCL0ItbWgk-xU4UPi4tML97HEzVCC2ATj89zJ9z5uH74Jvb4Vnx-4ROs4rzkJmyHguwTrZzrQuXVNGpdk4RBrMccQ1fmvjGtCwAydS5hKGqQ096gKvDLX_WF4ymnAI7n2De_czaI0wC7RfqK-CBg9DngtZSNNuB12AGoR3c505t_vE37LqxcEyRy22JL1qgwrvy_yVpKU2t4YERSJG20QoKzsdIOMvVaA9J9HJMEuXk8lyL31gITGBA4_b5FmpX05zQX06njpvYUIkw6Omey2a_fj5ELbadyxY03w3oahbih; __Secure-1PSIDTS={cookie_1psidts}; __Secure-3PSIDTS={cookie_3psidts}; SIDCC=AKEyXzXNtJLUkpkzefu-u92Dn8O26twdh5Lf1uhBaCuEUdzug2RW7_E2xbdB2BPG2MoUESoozUM; __Secure-1PSIDCC={cookie_1psidcc}; __Secure-3PSIDCC={cookie_3psidcc}; _ga_WC57KJ50ZZ=GS1.1.1712523895.4.1.1712525549.0.0.0"

    encoded_payload = get_encoded_description(final_prompt)
    split_payload = parse_qs(encoded_payload)

    f_req_payload = split_payload.get("f.req", [""])[0]
    at_payload = split_payload.get("at", [""])[0]
    r = requests.post(url, data={"f.req": f_req_payload, "at": at_payload}, headers=headers)
    numbers_only = [to_number(e) for e in r.text.split() if to_number(e) is not None]
    biggest_number = max(numbers_only) if numbers_only else None
    new_answer = r.text.split(str(biggest_number))[-1]
    if '\\",[\\"' in r.text:
        answer = (new_answer.split('\\",[\\"')[-1]).split('\\"],[]')[0]
        answer = unquote(answer.replace("\\n", "\n"))
        answer = "SELECT" + decode_unicode_escapes(answer).split("SELECT")[-1]
        answer = answer.split("\\")[0]
        print(answer)
        table_name = get_table_name_from_select(answer)
        if is_select_query(answer) and table_exists(table_name):
            houses = []
            with connection.cursor() as cursor:
                cursor.execute(answer)
                houses = cursor.fetchall()
                final_resp = []
                for house in houses:
                    house_instance = House.objects.filter(pk=house[0]).first()
                    final_resp.append(house_instance)
                    if user and not isinstance(user, AnonymousUser):
                        Searchable.objects.update_or_create(user=user, house=house_instance)
            serializer = HouseSerializer(final_resp, many=True)
            return Response(serializer.data)
    return Response({'error': "Coudn't Query Your Description"}, status=status.HTTP_400_BAD_REQUEST)


@shared_task
def synonyms_search(prompt):
    env = environ.Env()
    environ.Env.read_env()
    url = f"{env('GEMENI_ENDPOINT')}{str(random.randint(1111837555828070089, 9999999999999999999))}&hl=fr&_reqid={str(random.randint(1000000, 9999999))}&rt=c"
    headers = {
        "Referer": env("GEMENI_REFERER"),
    }
    prompt_template = Prompt.objects.all().order_by("order").last()
    final_prompt = prompt_template.text.replace('{term_to_replace}', f'\"{prompt}\"')
    print("---------------------------------------")
    print(final_prompt)
    print("---------------------------------------")
    cookie_1psidts, cookie_3psidts, cookie_1psidcc, cookie_3psidcc = get_cookie()
    ua = UserAgent()
    headers['User-Agent'] = ua.random
    # headers["Cookie"] = f"SEARCH_SAMESITE=CgQIy5oB; _ga=GA1.1.1838195142.1710699097; SID=g.a000iAi0d1i_cMN21fdk7sY4S2mVLmaQY0VXieP0h1t2wfhFcG77cUQ1bhmOXUwMe-xKBtr_KgACgYKAV8SAQASFQHGX2Miiu2LQkYPsqOINi7WoBCesBoVAUF8yKoqaBkOSYgwHaF6HK_RRBgU0076; __Secure-1PSID=g.a000iAi0d1i_cMN21fdk7sY4S2mVLmaQY0VXieP0h1t2wfhFcG77vLxDiYTkY4qe-eUn5BcAngACgYKAfISAQASFQHGX2MiTbw9JwUXnA_m1ULGWsYH6BoVAUF8yKoaY_68XimZsYLaSTcAyDge0076; __Secure-3PSID=g.a000iAi0d1i_cMN21fdk7sY4S2mVLmaQY0VXieP0h1t2wfhFcG77D3BeFFH50o6FGeewaGUIcAACgYKAZcSAQASFQHGX2Mi1Lm5RQsl2vInR0K5cr8p5BoVAUF8yKqngQd151GsBYdhO_OxwCcf0076; HSID=AEZXNCdS_Itjp5bvs; SSID=AEX_l_ULObAreQ-uw; APISID=LtrqXbEs68KtIV7W/AmywXc6U1QbT1BA91; SAPISID=dRmITJ9HBc4KTksn/Ae515bnoKS9D6aBUf; __Secure-1PAPISID=dRmITJ9HBc4KTksn/Ae515bnoKS9D6aBUf; __Secure-3PAPISID=dRmITJ9HBc4KTksn/Ae515bnoKS9D6aBUf; __Secure-ENID=18.SE=U-lSXl_MW7cg8_DUJ_dPODNG3QaPB1ztC40plGwJq7kn3Z3qkT3YiHmByTqiPsQUzx93LVWu67FCWFHK1ueYIuY7Bi9ksZpsaaOAZ6wK3wn-yTFJTHTxB9ICbBDSzD35MdEWs-ZWsV0vCag_f_b9qzPXhZWR0lUz4Ac9HUPn_CB_iFkdKoeM58U4217VBgcUKtUtuVhBvjbsIpC4eqH4ytUHZJY_ljyMAYy9dghyLLs2mrE-uZHP7IC3-rwgDEzdcVWxHzlZgPE0448qTzpNowZr6CCZP8N77BYt4l6jbQ; AEC=AQTF6HxzLVTZWsN5rAIL5dc5jHT1GDSebgCFj1wGQa3uZQVNxBIci4GIwJ8; NID=513=HyI7OE2N4NoBnG2KYCL0ItbWgk-xU4UPi4tML97HEzVCC2ATj89zJ9z5uH74Jvb4Vnx-4ROs4rzkJmyHguwTrZzrQuXVNGpdk4RBrMccQ1fmvjGtCwAydS5hKGqQ096gKvDLX_WF4ymnAI7n2De_czaI0wC7RfqK-CBg9DngtZSNNuB12AGoR3c505t_vE37LqxcEyRy22JL1qgwrvy_yVpKU2t4YERSJG20QoKzsdIOMvVaA9J9HJMEuXk8lyL31gITGBA4_b5FmpX05zQX06njpvYUIkw6Omey2a_fj5ELbadyxY03w3oahbih; __Secure-1PSIDTS={cookie_1psidts}; __Secure-3PSIDTS={cookie_3psidts}; SIDCC=AKEyXzXNtJLUkpkzefu-u92Dn8O26twdh5Lf1uhBaCuEUdzug2RW7_E2xbdB2BPG2MoUESoozUM; __Secure-1PSIDCC={cookie_1psidcc}; __Secure-3PSIDCC={cookie_3psidcc}; _ga_WC57KJ50ZZ=GS1.1.1712523895.4.1.1712525549.0.0.0"
    headers["Cookie"] = f"_ga=GA1.1.1931357345.1710366960; HSID=AGCEtFd8XunxmeoHs; SSID=Ak4_Vm52TCb3Y2DjJ; APISID=aFSkbaCc_OOgunjT/A_k10zn7gOVl3_Mf1; SAPISID=XCs-xUfZr2YMytdn/AfLsBCxfj_2oTpHnj; __Secure-1PAPISID=XCs-xUfZr2YMytdn/AfLsBCxfj_2oTpHnj; __Secure-3PAPISID=XCs-xUfZr2YMytdn/AfLsBCxfj_2oTpHnj; SID=g.a000jwg8nscu7uDTAenmjvDgSX5wFiSCh0bnvScb6VmJ13BrWJn9bnUFP2eBZTNXkzMI2FcIGQACgYKAVASAQASFQHGX2Min9Yuh3O5OSQFb74xY6Hn_BoVAUF8yKqspXaGjniTxigHruBeOmB90076; __Secure-1PSID=g.a000jwg8nscu7uDTAenmjvDgSX5wFiSCh0bnvScb6VmJ13BrWJn9h-XXjTLAQl3hiCM19YRx_wACgYKAR8SAQASFQHGX2MiWZKjVMY5WU4jXYUAIUfJJRoVAUF8yKq2bCIbcCe_8GTYEIwg6rBL0076; __Secure-3PSID=g.a000jwg8nscu7uDTAenmjvDgSX5wFiSCh0bnvScb6VmJ13BrWJn9i_ZjpEAZpeJzTs23zZF76gACgYKAcgSAQASFQHGX2Min7IFtc3SUwwiod8zZc0QjRoVAUF8yKrmepaMQefa63mKEkTTKeKu0076; SEARCH_SAMESITE=CgQInZsB; __Secure-BUCKET=CPwC; OGPC=19036484-1:; __Secure-ENID=20.SE=JI4SkWcfbgO11aSwFzg9JUdJPug8AMyOsjWFm3j0q6UG1VTubsz2OJ5vU3utbXiNJQ9CPNJUC5E2DzeU0OYfgekuTKAkHghaw78mLzwa_IM2M49-fI-W4Ea7QOGAUDA32mZv8kVOPjEVSIzuP5HWnnJ5NH6Pu6sQhOjK01aBmP5pMMziMQoveAmBzkur3pRiobmnX0v6g1KtaxTuMMQgvhWYEop7VvT0UfPpPnM9MRqAfnrHpW7z2l4yD2xeK5T5IouDi4Gh9UoG0KTjIFqYqtNMM15ysbCId2jy0eNcL5gWZCTLp9EWGt_pOfSFEN966pL4OQpCNK0basahA9bl; AEC=AQTF6Hyl--yqJqBipRZ5Hb27dGgIXkK9qeSdCMOwXhK8u9EqfLvZHV06gA; NID=515=XUKE5lxEG-K0y9Hq9Q72qZxj8HY2zhPAVeLaHk7PwwoYjFFjXXgX23bvUv707RiqgWB-2nfxLlvuDhN0wKmslWGtUp05kdJTEPoi6wxy-Q9tyWaQk5pIh-CLGu5L3G8RoGBmYzAZqFaxYcT-nxgCtu89HZZ3VE49tqtCY6bOEjc2RsDK_wieS1lZTWGS5p58qKALhNOJgHAWC1ucDhD4vnKOvcFRI33Kvf0sxEKcFqaXUXnpzENpH0uqvi6__8hXHJgXqP9TykuRbY3uQRBWbC4D5t-qpqjnntvXbAtBLm77iu9GdyEdf_k_JVTYEymnAJG030Dnqvk_jDv5kkpx6mBTr01P0sB8BsRE4qqol_XzydWLlJQ22V1FqTWBZkRhGqcAUJMYWL7HP-Ti2qgvZn_PkrNdtiIprFPdE7idwKpHWSuGoP01tboJxtdMKpZnbvd6ysP2yIBTnAUbLSDrFaOtT0JRvk8QO_E8l89VtWrwYVC6c1kLIGiBGJ67NPw9pNTUp_Cbmpuu7S1bjFf4fatnLGoP7_WY7cjiUnJ4UlVdGl3lh5xltxeKrsFtg_ep2WlAeNpf2LHscgzZBFPcZQ; __Secure-1PSIDTS={cookie_1psidts}; __Secure-3PSIDTS={cookie_3psidts}; SIDCC=AKEyXzUfBM-Xb8TxLUT5yaEsjNFpu50-O0nauGembyGcbBFcPACaX86c8VkvoICp3ufEWDDKNcI; __Secure-1PSIDCC={cookie_1psidcc}; __Secure-3PSIDCC={cookie_3psidcc}; _ga_WC57KJ50ZZ=GS1.1.1718641044.13.1.1718641177.0.0.0"
    encoded_payload = get_encoded_prompt(final_prompt)
    split_payload = parse_qs(encoded_payload)
    f_req_payload = split_payload.get("f.req", [""])[0]
    at_payload = split_payload.get("at", [""])[0]
    r = requests.post(url, data={"f.req": f_req_payload, "at": at_payload}, headers=headers)
    print(r.text)
    numbers_only = [to_number(e) for e in r.text.split() if to_number(e) is not None]
    biggest_number = max(numbers_only) if numbers_only else None
    new_answer = r.text.split(str(biggest_number))[-1]
    if '\\",[\\"' in r.text:
        answer = (new_answer.split('\\",[\\"')[-1]).split('\\"],[]')[0]
        answer = unquote(answer.replace("\\n", "\n"))
        words = answer.split("\n")
        print(words)
        if len(words) > 3:
            cleaned_words = [word[:-1].strip() if word.endswith("\\") else word.strip() for word in words]
            word_exist = Synonyms.objects.filter(original_word=prompt.lower()).first()
            if not word_exist:
                my_instance = Synonyms.objects.create(original_word=prompt)
                my_instance.set_synonyms(cleaned_words)
                my_instance.save()