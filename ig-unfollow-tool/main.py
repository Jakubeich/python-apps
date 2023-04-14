import time
import requests
from PIL import Image as PILImage
from PIL import ImageTk
from io import BytesIO
from tkinter import *
from tkinter import messagebox, ttk
from instagram_private_api import Client, ClientCompatPatch
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

# Disable SSL warnings
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
    
# End of disable SSL warnings
session = requests.Session()
session.mount('https://', TLSAdapter())

def login(username, password):
    try:
        api = Client(username, password)
        return api
    except Exception as e:
        print(f"Error logging in: {e}")
        return None

def get_following(api):
    user_id = api.authenticated_user_id
    following = api.user_following(user_id, api.generate_uuid())['users']
    return following

def unfollow(api, user_id):
    try:
        api.friendships_destroy(user_id)
        print(f"Unfollowed user with ID: {user_id}")
    except Exception as e:
        print(f"Error unfollowing user with ID {user_id}: {e}")

def start_unfollowing():
    username = username_entry.get()
    password = password_entry.get()

    api = login(username, password)
    if api:
        following = get_following(api)
        show_following(api, following)
    else:
        messagebox.showerror("Error", "Failed to log in. Check your username and password.")
        
def refresh_list(api, list_frame, user_vars):
    for widget in list_frame.winfo_children():
        widget.destroy()

    following = get_following(api)
    user_vars.clear()
    user_vars.update({user['pk']: IntVar() for user in following})

    for index, user in enumerate(following):
        response = session.get(user['profile_pic_url'])
        img_data = response.content
        img = PILImage.open(BytesIO(img_data)).resize((64, 64))
        img = ImageTk.PhotoImage(img)

        image_label = Label(list_frame, image=img)
        image_label.image = img
        image_label.grid(row=index, column=0, padx=10, pady=10)

        username_label = Label(list_frame, text=user['username'], font=('Arial', 12))
        username_label.grid(row=index, column=1, pady=10)

        checkbutton = Checkbutton(list_frame, variable=user_vars[user['pk']])
        checkbutton.grid(row=index, column=2, padx=10, pady=10)

def show_following(api, following):
    top = Toplevel(root)
    top.title("Following List")
    top.geometry("400x600")

    frame = Frame(top)
    frame.pack(fill=BOTH, expand=1)

    canvas = Canvas(frame)
    canvas.pack(side=LEFT, fill=BOTH, expand=1)

    scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    list_frame = Frame(canvas)
    canvas.create_window((0, 0), window=list_frame, anchor="nw")

    user_vars = {user['pk']: IntVar() for user in following}

    for index, user in enumerate(following):
        response = requests.get(user['profile_pic_url'])
        img_data = response.content
        img = PILImage.open(BytesIO(img_data)).resize((64, 64))
        img = ImageTk.PhotoImage(img)

        image_label = Label(list_frame, image=img)
        image_label.image = img
        image_label.grid(row=index, column=0, padx=10, pady=10)

        username_label = Label(list_frame, text=user['username'], font=('Arial', 12))
        username_label.grid(row=index, column=1, pady=10)

        checkbutton = Checkbutton(list_frame, variable=user_vars[user['pk']])
        checkbutton.grid(row=index, column=2, padx=10, pady=10)

    def unfollow_selected():
        unfollowed_users = []
        for user_id, var in user_vars.items():
            if var.get():
                unfollow(api, user_id)
                unfollowed_users.append(user_id)
                time.sleep(2)  # Add a delay between requests to avoid rate limiting

        # Refresh the list after unfollowing selected users
        if unfollowed_users:
            refresh_list(api, list_frame, user_vars)

    unfollow_button = Button(top, text="Unfollow", command=unfollow_selected)
    unfollow_button.pack(pady=10)

root = Tk()
root.title("Instagram Unfollower")
root.geometry("300x150")  # Adjust the window size

# Create a frame for better organization and padding
main_frame = Frame(root, padx=20, pady=20)
main_frame.pack()

username_label = Label(main_frame, text="Username:", font=("Arial", 12))
username_label.grid(row=0, column=0, sticky=W, pady=5)
username_entry = Entry(main_frame, font=("Arial", 12))
username_entry.grid(row=0, column=1, pady=5)

password_label = Label(main_frame, text="Password:", font=("Arial", 12))
password_label.grid(row=1, column=0, sticky=W, pady=5)
password_entry = Entry(main_frame, show="*", font=("Arial", 12))
password_entry.grid(row=1, column=1, pady=5)

start_button = Button(main_frame, text="Start", command=start_unfollowing, font=("Arial", 12))
start_button.grid(row=2, columnspan=2, pady=15)

root.mainloop()