# importing render and redirect
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

from .secret_key import API_KEY
# importing the openai API
import openai
# import the generated API key from the secret_key file

# loading the API key from the secret_key file
openai.api_key = API_KEY

first_flag =0
# this is the home view for handling home page logic
def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'core/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'core/simple_upload.html')
     
def home(request):
   
    try:
        # if the session does not have a messages key, create one
        if 'messages' not in request.session:
            request.session['messages'] = [
                
            ]
        if request.method == 'POST':

            with open("audio.mp3", "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    file = audio_file,
                    model = "whisper-1",
                    response_format="text",
                    language="en"
                )
            print(transcript)
            first_flag = 1
            # get the prompt from the form
            str1= "Here is who I am.'"
            auth= request.POST.get('author')
            bio= request.POST.get('bio')
            mission= request.POST.get('mission')
            if first_flag == 1:
                prompt = mission
            else :
                prompt= str1+auth+"."+bio+"'. "+mission        
            # get the temperature from the form
            temperature = float(request.POST.get('temperature', 0.1))
            # append the prompt to the messages list
            # set the session as modified
            request.session['messages'].append({"role": "user", "content": prompt})
            request.session.modified = True
            # call the openai API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=request.session['messages'],
                temperature=temperature,
                max_tokens=1000
            )
            # format the response
            formatted_response = response['choices'][0]['message']['content']
            # append the response to the messages list
            request.session['messages'].append({"role": "assistant", "content": formatted_response})
            request.session.modified = True
            # redirect to the home page
            context = {
                'messages': request.session['messages'],
                'prompt': '',
                'author' : auth,
                'input_flag' : 1,
                'bio' :bio,
                'temperature': temperature,
            }
            return render(request, 'assistant/home.html', context)
        else:
            # if the request is not a POST request, render the home page
            context = {
                'messages': request.session['messages'],
                'prompt': '',
                'temperature': 0.1,
            }
            return render(request, 'assistant/home.html', context)
    except Exception as e:
        print(e)
        # if there is an error, redirect to the error handler
        return redirect('error_handler')


def new_chat(request):
    # clear the messages list
    request.session.pop('messages', None)
    return redirect('home')


# this is the view for handling errors
def error_handler(request):
    return render(request, 'assistant/404.html')
