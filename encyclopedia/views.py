from django.shortcuts import render
from . import util
import markdown2
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import util
from django import forms
from django.contrib import messages
import random

class NewForm(forms.Form):
    title = forms.CharField(max_length=100)
    body = forms.CharField(widget=forms.Textarea(attrs={'name': 'body', 'rows': 15, "cols": 10}))

class EditForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'name': 'body', 'rows': 15, "cols": 10, 'required': True}))

# Index display all saved pages
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Display individual pages and thir contents
def page(request, title):
    contents = util.get_entry(title)
    if contents is not None:
        return render(request, "encyclopedia/page.html", {
            "contents": markdown2.markdown(contents),
            "title": title
        })
    else:
        return render(request, "encyclopedia/error.html")

# Search for query    
def search(request):

    # When search is submitted 
    if request.method == "POST":
        entries = util.list_entries()
        matches = []
        query = request.POST["q"]
        for entry in entries:
            # Query matched
            if query.lower() == entry.lower():
                return HttpResponseRedirect(reverse("encyclopedia:page", kwargs = {"title": entry}))
            # Similar search results
            elif query.lower() in entry.lower():
                matches.append(entry)
        
        # Render search results
        return render(request, "encyclopedia/results.html", {
            "matches": matches
        })
    
# create new page
def create(request):

    if request.method == "POST":
        newform = NewForm(request.POST)

        if newform.is_valid():
            title = newform.cleaned_data["title"]
            body = newform.cleaned_data["body"]
            entries = util.list_entries()

            # check for same titles
            for entry in entries:
                if entry.lower() == title.lower():
                    messages.error(request, "Title alredy exists")
                    return render(request, "encyclopedia/create.html", {
                        "form": newform
                    })
                
            # save if titles not same
            util.save_entry(title, body)
            return render(request, "encyclopedia/page.html", {
                "title": title,
                "contents": markdown2.markdown(body)
            })

        # invalid form
        else:
            messages.error(request, "Invalid form")
            return render(request, "encyclopedia/create.html", {
                "form": newform
            })


    # reached by get method
    else:
        newform = NewForm()
        return render(request, "encyclopedia/create.html", {
            "form": newform
        })
    
# Edit page
def edit(request, title):

    # Save edited form
    if request.method == "POST":
        editform = EditForm(request.POST)
        title = request.POST["title"]
        if editform.is_valid():
            body = editform.cleaned_data["body"]
            util.save_entry(title, body)
            return HttpResponseRedirect(reverse("encyclopedia:page", kwargs= {"title": title}))
        else:
            messages.error(request, "Invalid form")
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": editform
            })
        
    # Get request
    else:
        contents = util.get_entry(title)
        editform = EditForm()
        editform.initial["body"] = contents
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": editform
        })
    
# random page
def rand(request):
    entries = util.list_entries()
    choice = random.choice(entries)
    return HttpResponseRedirect(reverse("encyclopedia:page", kwargs={"title": choice}))
