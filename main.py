import re
import tkinter
import tkinter as tk
import urllib.request
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup


searchTerm = ""
numOfResults = 0
searchEngine = ""
url = ""
searchURL = ""
urlContent = []
urlContentTitle = []
pageIndex = 0


def radio_selection():
    global url
    global searchEngine
    if var.get() == 1:
        url = "https://www.google.com/search?q="
        searchEngine = "Google"
    elif var.get() == 2:
        url = "https://www.bing.com/search?q="
        searchEngine = "Bing"
    elif var.get() == 3:
        url = "https://html.duckduckgo.com/html/?q="
        searchEngine = "DuckDuckGo"


def get_results():
    global url
    global searchURL
    global urlContent
    global urlContentTitle
    global pageIndex

    urlContent = []
    urlContentTitle = []
    pageIndex = 0
    count = 0

    string = re.sub(' +', ' ', str(searchTerm))  # substitutes multiple spaces between words for single space
    searchURL = url + string.strip().replace(" ", "+")  # removes leading and trailing spaces

    if searchEngine != "Google":
        page = urllib.request.urlopen(searchURL).read()  # gets the url to read
        soup = BeautifulSoup(page, 'html.parser')

    if searchEngine == "Bing":  # calls the appropriate function to get results
        get_content_bing(soup, count)
    elif searchEngine == "DuckDuckGo":
        get_content_duckduckgo(soup, count)
    elif searchEngine == "Google":
        page = requests.get(searchURL)
        soup = BeautifulSoup(page.text, 'html.parser')
        get_content_google(soup, count)

    for i in range(len(urlContent)):
        print(urlContentTitle[i], " ", urlContent[i])

    resultsGUI = tk.Tk()
    resultsGUI.geometry("1200x800")
    resultsGUI.title("Results")

    textbox = tkinter.Text(master=resultsGUI, width=1200, height=800)

    for i in range(numOfResults):
        textbox.insert(tk.END, "\n{}:\n{}\n".format(urlContentTitle[i], urlContent[i]))

    textbox.pack()
    resultsGUI.mainloop()


def get_content_duckduckgo(soup, count):
    global urlContent
    global urlContentTitle
    global searchURL
    global pageIndex

    for url in soup.find_all('a'):  # gets all the links
        if "www." in str(url.get('href')):  # contains a website
            if str(url.get('href')) not in urlContent:  # has a link
                if count < numOfResults:  # hasn't reached the maximum pull request
                    # prettifies the results
                    uglyURL = str(url.get('href')).removeprefix("//duckduckgo.com/l/?uddg=").split("&", 1)
                    prettyURL = uglyURL[0]
                    # replaces ASCII characters
                    for item in (("%3A", ":"), ("%2F", "/"), ("%2D", "-"), ("%3F", "?"), ("%3D", "=")):
                        prettyURL = prettyURL.replace(*item)

                    if prettyURL not in urlContent:  # checks to see if the website is already stored
                        urlContent.append(prettyURL.strip())  # saves the url and title
                        urlContentTitle.append((str(url.get_text()).strip()))
                        count += 1

    if count < numOfResults:  # recursively goes to the next page
        pageIndex += 1
        if pageIndex == 1:
            searchURL = searchURL + "&s=" + str(pageIndex * 30) + "&dc=" + str(pageIndex * 30) + "&v=1&o=json&api=/d.js"
        else:
            uglyURL = searchURL.split("&s=")
            searchURL = uglyURL[0] + "&s=" + str(pageIndex * 30) + "&dc=" + str(
                pageIndex * 30) + "&v=1&o=json&api=/d.js"
        page = urllib.request.urlopen(searchURL).read()  # opens the new url for the next webpage
        soup = BeautifulSoup(page, 'html.parser')
        get_content_duckduckgo(soup, count)
    else:
        return
    return count


def get_content_google(soup, count):
    global urlContent
    global urlContentTitle
    global searchURL
    global pageIndex

    for url in soup.find_all('a'):
        if "https://" in str(url.get('href')):
            if "h3" in str(url):  # H3 are the results
                if str(url.get('href')) not in urlContent and str(url.get_text()) not in urlContentTitle:
                    if count < numOfResults:
                        urlContent.append(str(url.get('href')))
                        urlContentTitle.append((str(url.get_text())))
                        count += 1
    if count < numOfResults:
        pageIndex += 1
        if pageIndex == 1:
            searchURL = searchURL + "&start=" + str(pageIndex * 10)  # next page in iterations of 10
        else:
            searchURL = searchURL[:-2]  # removes the previous page number and adds the next
            searchURL = searchURL + str(pageIndex * 10)
        page = requests.get(searchURL)
        soup = BeautifulSoup(page.text, 'html.parser')
        get_content_google(soup, count)
    else:
        return
    return count


def get_content_bing(soup, count):  # same as duck duck go but for Bing
    global urlContent
    global urlContentTitle
    global searchURL
    global pageIndex

    # puts the unique urls in content list
    for url in soup.find_all('a'):
        if "https://" in str(url.get('href')):
            if str(url.get('href')) not in urlContent:
                if 'google' not in str(url.get('href')) and 'microsoft' not in str(url.get('href')):
                    if count < numOfResults:
                        urlContent.append(str(url.get('href')))
                        urlContentTitle.append((str(url.get_text())))
                        count += 1
    if count < numOfResults:
        pageIndex += 5
        if pageIndex == 5:
            searchURL = searchURL + "&first=" + str(pageIndex)
        else:
            uglyURL = searchURL.split("&first=")
            searchURL = uglyURL[0] + str("&first=") + str(pageIndex)
        page = urllib.request.urlopen(searchURL).read()
        soup = BeautifulSoup(page, 'html.parser')
        get_content_bing(soup, count)
    else:
        return
    return count


def check_inputs():
    if url != "":
        global searchTerm
        searchTerm = entry.get()
        entry.delete(0, tk.END)
        if searchTerm != "":
            global numOfResults
            numOfResults = int(comboBox.get())
            get_results()
        else:
            messagebox.showinfo("Warning", "Please enter a search term")
    else:
        messagebox.showinfo("Warning", "Please select a search engine.")


window = tk.Tk()  # creates the main GUI window
window.title("Search")
window.geometry("300x300")
window.resizable(0, 0)  # prevents resizing

radioFrame = tk.Frame()  # radio button frame
var = tk.IntVar()
searchEngineLabel = tk.Label(text="Select search engine below:", master=radioFrame)

# create the search engine radio buttons
r1 = ttk.Radiobutton(radioFrame, text="Google", variable=var, value=1, command=radio_selection)
r2 = ttk.Radiobutton(radioFrame, text="Bing", variable=var, value=2, command=radio_selection)
r3 = ttk.Radiobutton(radioFrame, text="DuckDuckGo", variable=var, value=3, command=radio_selection)

# adds the search engine label and buttons to the frame
searchEngineLabel.pack()
r1.pack(side=tk.LEFT, padx=5)
r2.pack(side=tk.LEFT, padx=5)
r3.pack(side=tk.LEFT, padx=5)
radioFrame.pack()  # adds radio button frame to the window

# creates the search label, entry box for user input, and number of results to display
searchFrame = tk.Frame()
searchLabel = ttk.Label(text="Enter search term:", master=searchFrame)
entry = ttk.Entry(searchFrame, width=40)
numberLabel = ttk.Label(text="Select number of results to display:", master=searchFrame)
n = tk.StringVar()
comboBox = ttk.Combobox(searchFrame, textvariable=n, width=5)
comboBox['values'] = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
comboBox.current(0)

# adds the search term and label to the frame
searchLabel.pack()
entry.pack()
numberLabel.pack(pady=10)
comboBox.pack()
searchFrame.pack(pady=30)

search = ttk.Button(master=window, text="Submit", command=check_inputs)
search.pack(pady=20)

window.mainloop()
