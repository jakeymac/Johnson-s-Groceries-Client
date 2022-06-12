import tkinter as tk
import tkinter.messagebox as tk_mb
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from requests import delete

class Main():
    def __init__(self,root):
        self.root = root
        self.main_menu()

        cred = credentials.Certificate("johnsons_groceries_authentication_key.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL":"https://johnson-s-groceries-default-rtdb.firebaseio.com/"
        })

        self.stock_ref = db.reference("stock")

    def main_menu(self):
        self.main_menu_frame = tk.Frame(self.root)
        self.main_menu_frame.pack()

        self.main_welcome_label = tk.Label(self.main_menu_frame ,text="Welcome to Johnson Groceries")
        self.main_welcome_label.grid(row=0,column=0,columnspan=2)

        self.main_create_receipt_button = tk.Button(self.main_menu_frame,text="Create Receipt",command=self.create_receipt_menu)
        self.main_create_receipt_button.grid(row=1,column=0)
        
        self.main_entire_stock_button = tk.Button(self.main_menu_frame,text="Check Entire Stock",command=self.entire_stock_window)
        self.main_entire_stock_button.grid(row=2,column=0)
        
        self.main_check_single_stock_label = tk.Label(self.main_menu_frame ,text="Enter an item name to check \nit's current stock: ")
        self.main_check_single_stock_label.grid(row=3,column=0)
        
        self.main_check_single_entry = tk.Entry(self.main_menu_frame )
        self.main_check_single_entry.grid(row=4,column=0)
        
        self.main_check_single_button = tk.Button(self.main_menu_frame ,text="Check Stock",command=self.check_single_stock)
        self.main_check_single_button.grid(row=5,column=0)

        self.single_stock_check_label = tk.Label(self.main_menu_frame)
        self.single_stock_check_label.grid(row=6,column=0)

        self.main_exit_button = tk.Button(self.main_menu_frame,text="Exit Program",command=self.exit_program)
        self.main_exit_button.grid(row=7,column=0)
        
        self.main_edit_stock_section_label = tk.Label(self.main_menu_frame,text="Edit Stock Below")
        self.main_edit_stock_section_label.grid(row=1,column=1)

        self.main_add_new_item_button = tk.Button(self.main_menu_frame,text="Add New Item",command=self.add_new_item_menu)
        self.main_add_new_item_button.grid(row=2,column=1,pady=12)
        
        self.main_delete_item_entry = tk.Entry(self.main_menu_frame)
        self.main_delete_item_entry.grid(row=3,column=1)

        self.main_delete_item_button = tk.Button(self.main_menu_frame,text="Delete Item",command=self.delete_item)
        self.main_delete_item_button.grid(row=4,column=1)

        self.main_edit_stock_entry = tk.Entry(self.main_menu_frame)
        self.main_edit_stock_entry.grid(row=5,column=1,pady=8)

        self.main_edit_stock_button = tk.Button(self.main_menu_frame,text="Edit Stock Quantity",command=self.edit_stock_menu)
        self.main_edit_stock_button.grid(row=6,column=1)

    def check_single_stock(self):
        item = self.main_check_single_entry.get()
        if item in self.stock_ref.get():
            item_stock = self.stock_ref.child(item).get().get("stock")
            if item_stock == 0:
                item_stock = "Out of Stock"

            self.single_stock_check_label.config(text=f"Current stock \nof {item}: {item_stock}")
            
        else:
            tk_mb.showinfo(title="Error",message="Sorry, I can't seem to find that item in our system. Try again!")
            self.single_stock_check_label.config(text="")

    def create_receipt_menu(self):
        self.close_main_menu()

        self.receipt_menu_frame = tk.Frame(self.root)
        self.receipt_menu_frame.pack()

        self.receipt_menu_label = tk.Label(self.receipt_menu_frame,text="Add items to your receipt")
        self.receipt_menu_label.grid(row=0,column=0,columnspan=3)

        self.receipt_item_name_label = tk.Label(self.receipt_menu_frame,text="Item Name:")
        self.receipt_item_name_label.grid(row=1,column=0)

        self.receipt_item_name_entry = tk.Entry(self.receipt_menu_frame)
        self.receipt_item_name_entry.grid(row=1,column=1,columnspan=2)

        self.receipt_item_quantity_label = tk.Label(self.receipt_menu_frame,text="Quantity:")
        self.receipt_item_quantity_label.grid(row=2,column=0)
        
        self.receipt_item_quantity_entry = tk.Entry(self.receipt_menu_frame)
        self.receipt_item_quantity_entry.grid(row=2,column=1)

        self.receipt_add_item_button = tk.Button(self.receipt_menu_frame,text="Add Item",command=self.receipt_add_item)
        self.receipt_add_item_button.grid(row=3,column=1)
        self.added_item_list = []
        self.item_quantity_var_list = []
        
        self.receipt_items_frame = tk.Frame(self.receipt_menu_frame)
        self.receipt_items_frame.grid(row=4,column=0,columnspan=3)

        self.receipt_back_button = tk.Button(self.receipt_menu_frame,text="Back",command=self.return_from_receipt_menu)
        self.receipt_back_button.grid(row=5,column=0)

        self.create_receipt_button = tk.Button(self.receipt_menu_frame,text="Create Receipt",command=self.create_receipt)
        self.create_receipt_button.grid(row=5,column=1)

    def create_receipt(self):
        final_total = 0
        display_string = ""

        for i in range(0,len(self.added_item_list)):
            item = self.added_item_list[i]
            price = float(self.stock_ref.child(item).get().get("price"))
            quantity = self.item_quantity_var_list[i].get()
            total = round(price * int(quantity),2)
            new_line = f"{item} x {quantity}: ${total}\n"
            display_string += new_line
            final_total += total

        display_string += f"Final total: ${round(final_total,2)}\n Would you like to finalize this purchase?"
        finalize_purchase = tk_mb.askquestion(title="Final Receipt",message=display_string)
        if finalize_purchase == "yes":
            self.remove_stock()

    def receipt_add_item(self):
        item = self.receipt_item_name_entry.get()
        quantity = self.receipt_item_quantity_entry.get()

        if item not in self.stock_ref.get():
            tk_mb.showinfo("Error","Sorry, we don't carry that item! Try again!")
        else:
            if item in self.added_item_list:
                tk_mb.showinfo("Sorry, that item has already been added. Try updating the quantity below")
            else:
                if int(quantity) > int(self.stock_ref.child(item).get().get("stock")):
                    tk_mb.showinfo("Error",f"Sorry, we don't have enough of that item in stock. The current stock of {item} is: {self.stock_ref.child(item).get().get('stock')}")
                else:
                    new_item_frame = tk.Frame(self.receipt_items_frame)
                    new_item_frame.pack()
                    price = self.stock_ref.child(item).get().get("price")
                    total = "$" + str(round(float(price) * int(quantity),2))

                    new_item_text = f"{item} - {price} x "
                    new_item_label = tk.Label(new_item_frame,text=new_item_text)
                    new_item_label.grid(row=0,column=0)

                    new_item_string_var = tk.StringVar()
                    new_item_string_var.set(quantity)
                    new_item_options = [str(i) for i in range(1,int(self.stock_ref.child(item).get().get("stock"))+1)]

                    new_item_total_label = tk.Label(new_item_frame,text=f"${total}")
                    new_item_total_label.grid(row=0,column=2)

                    new_item_quantity_menu = tk.OptionMenu(new_item_frame,new_item_string_var,*new_item_options,command=lambda x = new_item_string_var.get(), y = new_item_total_label,z=price:self.edit_receipt_quantity(x,y,z))
                    new_item_quantity_menu.grid(row=0,column=1)
                    
                    new_item_remove_button = tk.Button(new_item_frame,text="Remove",command=lambda:self.delete_item_from_receipt(new_item_frame,item,new_item_string_var))
                    new_item_remove_button.grid(row=0,column=3)

                    self.added_item_list.append(item)
                    self.item_quantity_var_list.append(new_item_string_var)

    def edit_receipt_quantity(self,new_quantity,item_total_label,price):
        item_total_label.config(text=f"${round(float(price) * int(new_quantity),2)}")

    def delete_item_from_receipt(self,item_frame,item,stringvar):
        item_frame.destroy()
        self.added_item_list.remove(item)
        self.item_quantity_var_list.remove(stringvar)

    def remove_stock(self):
        print("Removinggg")
        for i in range(len(self.added_item_list)):
            item = self.added_item_list[i]
            old_stock = self.stock_ref.child(item).get().get("stock")
            new_stock = int(old_stock) - int(self.item_quantity_var_list[i].get())
            self.stock_ref.child(item).update({"stock":str(new_stock)})
        
    def add_new_item_menu(self):
        self.close_main_menu()

        self.add_new_item_menu_frame = tk.Frame(self.root)
        self.add_new_item_menu_frame.pack()

        self.add_new_item_top_label = tk.Label(self.add_new_item_menu_frame,text="Here you can add new items to our stock")
        self.add_new_item_top_label.grid(row=0,column=0,columnspan=2)

        self.add_new_item_name_label = tk.Label(self.add_new_item_menu_frame,text="Name:")
        self.add_new_item_name_label.grid(row=1,column=0)

        self.add_new_item_name_entry = tk.Entry(self.add_new_item_menu_frame)
        self.add_new_item_name_entry.grid(row=1,column=1)

        self.add_new_item_price_label = tk.Label(self.add_new_item_menu_frame,text="Price:")
        self.add_new_item_price_label.grid(row=2,column=0)

        self.add_new_item_price_entry = tk.Entry(self.add_new_item_menu_frame)
        self.add_new_item_price_entry.grid(row=2,column=1)

        self.add_new_item_stock_label = tk.Label(self.add_new_item_menu_frame,text="Quantity:")
        self.add_new_item_stock_label.grid(row=3,column=0)

        self.add_new_item_stock_entry = tk.Entry(self.add_new_item_menu_frame)
        self.add_new_item_stock_entry.grid(row=3,column=1)

        self.add_new_item_info_label = tk.Label(self.add_new_item_menu_frame,text="Info:")
        self.add_new_item_info_label.grid(row=4,column=0)
        
        self.add_new_item_info_entry = tk.Entry(self.add_new_item_menu_frame)
        self.add_new_item_info_entry.grid(row=4,column=1)

        self.add_new_item_button = tk.Button(self.add_new_item_menu_frame,text="Add Item",command=self.add_new_item_from_menu)
        self.add_new_item_button.grid(row=5,column=1)

        self.add_new_item_exit_button = tk.Button(self.add_new_item_menu_frame,text="Back",command=self.exit_new_item_menu)
        self.add_new_item_exit_button.grid(row=5,column=0)

    def add_new_item_from_menu(self):
        if self.add_new_item_name_entry.get() in self.stock_ref.get():
            tk_mb.showinfo("Sorry, that item already exists in our stock")

        else:
            self.stock_ref.child(self.add_new_item_name_entry.get()).set({
                "stock": self.add_new_item_stock_entry.get(),
                "price": self.add_new_item_price_entry.get(),
                "info": self.add_new_item_info_entry.get()
            })

            tk_mb.showinfo(message=f"Success! We've added {self.add_new_item_name_entry.get()} to our stock!")
            self.add_new_item_name_entry.delete(0,tk.END)
            self.add_new_item_stock_entry.delete(0,tk.END)
            self.add_new_item_price_entry.delete(0,tk.END)
            self.add_new_item_info_entry.delete(0,tk.END)

    def delete_item(self):
        item_to_delete = self.main_delete_item_entry.get()
        if item_to_delete not in self.stock_ref.get():
            tk_mb.showinfo(title="Error",message="Sorry, I can't seem to find that item in our system. Try again!")
        else:
            delete_item_message_box = tk_mb.askquestion("Delete Item",f"Are you sure you want to delete the item '{item_to_delete}'?")
            if delete_item_message_box == "yes":
                self.stock_ref.child(item_to_delete).delete()

    def edit_stock_menu(self):
        self.item_to_edit = self.main_edit_stock_entry.get()
        if self.item_to_edit not in self.stock_ref.get():
            tk_mb.showinfo(title="Error",message="Sorry, I can't seem to find that item in our system. Try again!")

        else:
            item = self.item_to_edit
            price = self.stock_ref.child(item).get().get("price")
            quantity = str(self.stock_ref.child(item).get().get("stock"))
            info = self.stock_ref.child(item).get().get("info")

            self.close_main_menu()
            self.edit_stock_menu_frame = tk.Frame(self.root)
            self.edit_stock_menu_frame.pack()

            self.edit_menu_item_label = tk.Label(self.edit_stock_menu_frame,text=f"Editing {item}")
            self.edit_menu_item_label.grid(row=0,column=0,columnspan=2)

            self.edit_menu_stock_label = tk.Label(self.edit_stock_menu_frame,text="Stock:")
            self.edit_menu_stock_label.grid(row=1,column=0)

            self.edit_menu_stock_entry = tk.Entry(self.edit_stock_menu_frame)
            self.edit_menu_stock_entry.grid(row=1,column=1)
            self.edit_menu_stock_entry.insert(0,quantity)

            self.edit_menu_price_label = tk.Label(self.edit_stock_menu_frame,text="Price:")
            self.edit_menu_price_label.grid(row=2,column=0)
            
            self.edit_menu_price_entry = tk.Entry(self.edit_stock_menu_frame)
            self.edit_menu_price_entry.grid(row=2,column=1)
            self.edit_menu_price_entry.insert(0,price)

            self.edit_menu_info_label = tk.Label(self.edit_stock_menu_frame,text="Info:")
            self.edit_menu_info_label.grid(row=3,column=0)

            self.edit_menu_info_entry = tk.Entry(self.edit_stock_menu_frame)
            self.edit_menu_info_entry.grid(row=3,column=1)
            self.edit_menu_info_entry.insert(0,info)

            self.edit_menu_return_button = tk.Button(self.edit_stock_menu_frame,text="Return to Main Menu",command=self.close_edit_stock_menu)
            self.edit_menu_return_button.grid(row=4,column=0)

            self.edit_menu_save_button = tk.Button(self.edit_stock_menu_frame,text="Save",command=self.edit_stock_from_menu)
            self.edit_menu_save_button.grid(row=4,column=1)    

    def edit_stock_from_menu(self):
        print("editing")
        self.stock_ref.child(self.item_to_edit).update({
            "stock": self.edit_menu_stock_entry.get(),
            "price": self.edit_menu_price_entry.get(),
            "info": self.edit_menu_info_entry.get()
        })

    def exit_new_item_menu(self):
        self.add_new_item_menu_frame.destroy()
        self.main_menu()

    def close_edit_stock_menu(self):
        self.edit_stock_menu_frame.destroy()
        self.main_menu()

    def entire_stock_window(self):
        self.close_main_menu()
        self.entire_stock_window_frame = tk.Frame(self.root)
        self.entire_stock_window_frame.pack()

        vertical = tk.Scrollbar(self.entire_stock_window_frame,orient="vertical")
        vertical.pack(side=tk.RIGHT,fill=tk.Y)

        stock_text_widget = tk.Text(self.entire_stock_window_frame,width=45,height=25,wrap=tk.NONE,yscrollcommand=vertical.set)

        for item in self.stock_ref.get():
            price = self.stock_ref.child(item).get().get("price")
            stock = self.stock_ref.child(item).get().get("stock")
            if stock == 0:
                stock = "Out of stock"
            else:
                stock = str(stock) + " in stock"

            stock_text_widget.insert(tk.END,f"{item} - {price} - {stock}\n")

        stock_text_widget.pack()  

        self.return_to_main_menu_button = tk.Button(self.entire_stock_window_frame,text="Return to Main Menu",command=self.close_entire_stock_window)
        self.return_to_main_menu_button.pack()

    def return_from_receipt_menu(self):
        print("back")
        if len(self.added_item_list) > 0:
            leave = tk_mb.askquestion(message="Are you sure you want to leave?")
            if leave == "yes":
                self.receipt_menu_frame.destroy()
                self.main_menu()
        else:
            self.receipt_menu_frame.destroy()
            self.main_menu()

    def close_entire_stock_window(self):
        self.entire_stock_window_frame.destroy()
        self.main_menu()

    def close_main_menu(self):
        self.main_menu_frame.destroy()

    def exit_program(self):
        exit_window = tk_mb.askquestion("Exit","Are you sure you want to close the program?")
        if exit_window == "yes":
            self.root.destroy()

root = tk.Tk()
main = Main(root)
main.root.mainloop()
