def basit_generator():
    print("İlk değer üretiliyor...")
    yield {"message":"Deneme","done":False}
    
    print("İkinci değer üretiliyor...")
    yield {"message":"Deneme","done":False}
    
    print("Son değer üretiliyor...")
    yield {"message":"Deneme","done":False}
    
    print("Son değer üretiliyor...")
    yield {"message":"Deneme","done":True}
    
    print("Son değer üretiliyor...")
    yield {"message":"Deneme3","done":True}

    
    print("Son değer üretiliyor...")
    yield {"message":"Deneme2","done":True}


# Generator objesini oluşturuyoruz
gen = basit_generator()


while True:
    data = next(gen)
    print(data)
    if data['done'] == True:
        break