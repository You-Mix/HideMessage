from django.shortcuts import render, redirect
from stegano import lsb
import secrets
import base64
from .models import *
import os
from django.core.files.storage import default_storage
import magic 
import stepic
from PIL import Image
import shutil


# Create your views here.
def index(request):
    
    chemin_dossier = 'hide_message/static/encoded_images/'
    shutil.rmtree(chemin_dossier)
    shutil.os.makedirs(chemin_dossier)

    return render(request,'index.html')


def page_encodage(request):
    return render(request,'encodage.html')


def page_decodage(request):
    return render(request,'decodage.html')






# Fonction pour encoder le texte dans une image avec une clé de décodage
def encode_text_in_image(request):
    if request.method == 'POST':
        text_to_hide = request.POST.get('message_text', '')
        input_image = request.FILES.get('image', None)
        decoding_key = request.POST.get('decode_key', '')

        #decoding_key = secrets.token_hex(16)
        input_image_path = os.path.join('hide_message/static/encoded_images/', os.path.basename(input_image.name))

        with default_storage.open(input_image_path, 'wb') as input_image_file:
            input_image_file.write(input_image.read())


        png_path = 'hide_message/static/encoded_images/' + os.path.basename(input_image.name).replace('.jpg', '.png')

        # Ouvrir l'image depuis le chemin
        image = Image.open(input_image_path)
        image.save(png_path)
        # Convertir le texte à cacher en bytes
        data_to_hide = (decoding_key + text_to_hide).encode('utf-8')

        # Encoder le texte dans l'image
        secret = stepic.encode(image, data_to_hide)

        # Sauvegarder l'image encodée
        secret.save(png_path)

        # Chemin absolu de l'image encodée
        output_path = os.path.abspath(png_path)
        print(output_path)

        context = {
            'decoding_key': decoding_key,
            'output_image': os.path.join('encoded_images/', os.path.basename(input_image.name).replace('.jpg', '.png')),
        }

        return render(request, 'resultat_encodage.html', context)
    else:
        return redirect('page_encodage')

# Fonction pour décoder le texte à partir d'une image avec une clé de décodage
def decode_text_from_image(request):
    if request.method == 'POST':
        encoded_image = request.FILES.get('image_to_decode', None)
        decoding_key = request.POST.get('key', '')

        encoded_image_path = os.path.join('hide_message/static/encoded_images/', os.path.basename(encoded_image.name))

        with default_storage.open(encoded_image_path, 'wb') as encoded_image_file:
            encoded_image_file.write(encoded_image.read())
        
        #try:
        with Image.open(encoded_image) as img:
            data = stepic.decode(img)

        extracted_key, hidden_message = data[:len(decoding_key)], data[len(decoding_key):]  # La clé est les 32 premiers caractères

        print(hidden_message)
        if extracted_key == decoding_key:
            decoded_message = hidden_message
        else:
            decoded_message = "Clé de décodage incorrecte."
        #except Exception as e:
        #    decoded_message = f"Erreur lors du décodage : {str(e)}"
        #    isText, isImage, isDoc = False, False, False

        context = {
            'decoded_message': decoded_message,
            'isText': True,
            'encoded_image' : os.path.join('encoded_images/', os.path.basename(encoded_image.name)),
            'decoding_key' : decoding_key,
        }

        return render(request, 'resultat_decodage.html', context)
    else:
        return redirect('page_decodage')




# Fonction pour encoder une image avec une clé de décodage
def encode_image_in_image(request):
    if request.method == 'POST':
        image_to_hide = request.FILES.get('image_to_hide', None)
        input_image = request.FILES.get('output_image', None)
        decoding_key = request.POST.get('decode_key', '')

        input_image_path = os.path.join('hide_message/static/encoded_images/', os.path.basename(input_image.name))
        image_to_hide_path = os.path.join('hide_message/static/encoded_images/', os.path.basename(image_to_hide.name))

        with default_storage.open(input_image_path, 'wb') as input_image_file:
            input_image_file.write(input_image.read())

        with default_storage.open(image_to_hide_path, 'wb') as image_to_hide_file:
            image_to_hide_file.write(image_to_hide.read())

        png_path = 'hide_message/static/encoded_images/' + os.path.basename(input_image.name).replace('.jpg', '.png')
        png_path1 = 'encoded_images/' + os.path.basename(input_image.name).replace('.jpg', '.png')
        # Ouvrir l'image depuis le chemin
        input_image = Image.open(input_image_path)

        # Ouvrir l'image à cacher
        image_to_hide = Image.open(image_to_hide_path)

        # Encoder le texte dans l'image
        image_data = stepic.encode(image_to_hide, decoding_key.encode('utf-8'))

        # Sauvegarder l'image encodée
        #image_data.save(png_path)


        # Encoder l'image dans l'image principale
        input_image.paste(image_data, (0, 0))

        # Sauvegarder l'image encodée
        input_image.save(png_path)

        # Chemin absolu de l'image encodée
        output_path = os.path.abspath(png_path)
        print(output_path)

        context = {
            'decoding_key': decoding_key,
            'output_image': png_path1,
        }

        return render(request, 'resultat_encodage.html', context)
    else:
        return redirect('page_encodage')




# Fonction pour décoder une image avec une clé de décodage
def decode_image_from_image(request):
    if request.method == 'POST':
        encoded_image = request.FILES.get('image_to_decode', None)
        decoding_key = request.POST.get('key', '')

        encoded_image_path = os.path.join('hide_message/static/encoded_images/', os.path.basename(encoded_image.name))

        with default_storage.open(encoded_image_path, 'wb') as encoded_image_file:
            encoded_image_file.write(encoded_image.read())
        
        try:
            with Image.open(encoded_image_path) as img:
                # Extraire l'image cachée
                image_data = img.tobytes()
                
                # Extraire la clé et l'image cachée
                #extracted_key, hidden_image_data = image_data[:len(decoding_key)], image_data[len(decoding_key):]

                hidden_image_data = image_data
                # Créer une image à partir des données extraites
                width, height = img.size
                hidden_image = Image.frombytes('RGB', (width, height), hidden_image_data)

                extracted_key = stepic.decode(hidden_image)

                print(extracted_key)

                if extracted_key == decoding_key:
                    
                    # Sauvegarder l'image cachée
                    hidden_image_path = os.path.join('hide_message/static/decoded_images/', f'decoded_{os.path.basename(encoded_image.name)}')
                    hidden_image.save(hidden_image_path)

                    print(hidden_image_path)

                    context = {
                        'decoded_image_path': os.path.join('decoded_images/', f'decoded_{os.path.basename(encoded_image.name)}'),
                        'decoding_key': decoding_key,
                        'isImage' : True,
                        'encoded_image' : os.path.join('encoded_images/', os.path.basename(encoded_image.name)),
                        'decoding_key' : decoding_key,
                    }
                else:
                    context = {
                        'decoded_image_path': None,
                        'decoding_key': decoding_key,
                        'isImage' : True,
                        'encoded_image' : os.path.join('encoded_images/', os.path.basename(encoded_image.name)),
                        'decoding_key' : decoding_key,
                    }
        except Exception as e:
            context = {
                'decoded_image_path': None,
                'decoding_key': decoding_key,
                'error_message': f"Erreur lors du décodage : {str(e)}",
                'encoded_image' : os.path.join('encoded_images/', os.path.basename(encoded_image.name)),
                'decoding_key' : decoding_key,
            }

        return render(request, 'resultat_decodage.html', context)
    else:
        return redirect('page_decodage')


# Fonction pour encoder un document avec une clé de décodage
def encode_doc_in_image(request):
    if request.method == 'POST':
        input_doc = request.FILES['input_doc']
        output_image = request.FILES['output_image']

        image_to_hide_path = os.path.join('encoded_images/',os.path.basename(input_doc.name))
        decoding_key = secrets.token_hex(16)


        output_image_path = os.path.join('encoded_images/',os.path.basename(output_image.name))

        with default_storage.open(output_image_path, 'wb') as output_image_file:
            output_image_file.write(output_image.read())


        # Concaténer la clé de décodage avec les données de l'image
        data_to_hide = decoding_key + base64.b64encode(input_doc.read()).decode('utf-8')

        secret = lsb.hide(output_image, data_to_hide)
        secret.save(output_image_path)
        
        context = {
            'decoding_key' : decoding_key,
            'output_image' : output_image_path,
        }

        return render(request, 'resultat_encodage.html', context)
    else:
        return redirect('page_encodage')


# Fonction pour décoder un document avec une clé de décodage
def decode_doc_from_image(encoded_image, decoding_key, output_document_path):
    #data = helpers.decode_binary(lsb.reveal(encoded_image))
    extracted_key, extracted_document_data = data[:32], data[32:]

    if extracted_key == decoding_key:
        with open(output_document_path, 'wb') as document:
            document.write(extracted_document_data)
    else:
        print("Clé de décodage incorrecte.")
