from seller import Seller

import psycopg2

from config import read_config
from messages import *

"""
    Splits given command string by spaces and trims each token.
    Returns token list.
"""
def tokenize_command(command):
    tokens = command.split(" ")
    return [t.strip() for t in tokens]

class Mp2Client:
    def __init__(self, config_filename):
        self.db_conn_params = read_config(filename=config_filename, section="postgresql")
        self.conn = None

    """
        Connects to PostgreSQL database and returns connection object.
    """
    def connect(self):
        self.conn = psycopg2.connect(**self.db_conn_params)
        self.conn.autocommit = False

    """
        Disconnects from PostgreSQL database.
    """
    def disconnect(self):
        self.conn.close()

    """
        Prints list of available commands of the software.
    """
    def help(self):
        # prints the choices for commands and parameters
        print("\n*** Please enter one of the following commands ***")
        print("> help")
        print("> sign_up <seller_id> <subscriber_key> <zip_code> <city> <state> <plan_id>")
        print("> sign_in <seller_id> <subscriber_key>")
        print("> sign_out")
        print("> show_plans")
        print("> show_subscription")
        print("> change_stock <product_id> <add or remove> <amount>")
        print("> show_quota")
        print("> subscribe <plan_id>")
        print("> ship <product_id_1> <product_id_2> <product_id_3> ... <product_id_n>")
        print("> calc_gross")
        print("> show_cart <customer_id>")
        print("> change_cart <customer_id> <product_id> <seller_id> <add or remove> <amount>")
        print("> purchase_cart <customer_id>")
        print("> quit")
    
    """
        Saves seller with given details.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def sign_up(self, seller_id, sub_key, zip, city, state, plan_id):
        # TODO: implement this function
        try:
            # Check if the seller with the same seller_id already exists
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM sellers WHERE seller_id = %s", (seller_id,))
            existing_seller = cursor.fetchone()
            if existing_seller is not None:
                return False, CMD_EXECUTION_FAILED
            cursor.close()

    
            # Insert the new seller into the sellers table
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO sellers VALUES (%s, %s, %s, %s)",
                (seller_id, zip, city, state)
                
            )
            cursor.execute(
                "INSERT INTO seller_subscription VALUES (%s, %s, %s, %s)",
                (seller_id, sub_key, 0, plan_id)
                
            )
            self.conn.commit()
            cursor.close()

           
            return True, CMD_EXECUTION_SUCCESS

        except psycopg2.Error as e:
            print("Error creating new seller:", e)
            return False, CMD_EXECUTION_FAILED
            

    """
        Retrieves seller information if seller_id and subscriber_key is correct and seller's session_count < max_parallel_sessions.
        - Return type is a tuple, 1st element is a seller object and 2nd element is the response message from messages.py.
        - If seller_id or subscriber_key is wrong, return tuple (None, USER_SIGNIN_FAILED).
        - If session_count < max_parallel_sessions, commit changes (increment session_count) and return tuple (seller, CMD_EXECUTION_SUCCESS).
        - If session_count >= max_parallel_sessions, return tuple (None, USER_ALL_SESSIONS_ARE_USED).
        - If any exception occurs; rollback, do nothing on the database and return tuple (None, USER_SIGNIN_FAILED).
    """
    def sign_in(self, seller_id, sub_key):
        # TODO: implement this function
            try:
                # Check if the seller credentials are valid
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM seller_subscription WHERE seller_id = %s AND subscriber_key = %s", (seller_id, sub_key))
                seller = cursor.fetchone()
                cursor.close()

                if seller is None:
                    return None, USER_SIGNIN_FAILED

                # Check if the seller is out of sessions
                cursor = self.conn.cursor()
                cursor.execute("select * from subscription_plans where plan_id = %s", (seller[3],))
                plan = cursor.fetchone()
                cursor.close()
               
                # print seller and plan


                if(seller[2] >= plan[2]):
                    return None, USER_ALL_SESSIONS_ARE_USED
                
               

                # Increment the session count for the seller
                cursor = self.conn.cursor()
                cursor.execute("UPDATE seller_subscription SET session_count = session_count + 1 WHERE seller_id = %s", (seller_id,))
                self.conn.commit()
                cursor.close()


                return seller[0], CMD_EXECUTION_SUCCESS
            except psycopg2.Error as e:
                print("Error signing in:", e)
                return None, CMD_EXECUTION_FAILED
               


    """
        Signs out from given seller's account.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Decrement session_count of the seller in the database.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def sign_out(self, seller):
        # TODO: implement this function
        try:
            # Fetch the seller's session count
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_subscription WHERE seller_id = %s", (seller,))
            seller1= cursor.fetchone()
            session_count = seller1[2]
            cursor.close()


            

            # Check if the session count is at least 0
            if session_count < 0:
                print("ERROR: Can not execute the given command.")
                return False, CMD_EXECUTION_FAILED

            # Decrement the session count
            cursor = self.conn.cursor()
            cursor.execute("UPDATE seller_subscription SET session_count = session_count - 1 WHERE seller_id = %s", (seller,))
            self.conn.commit()
            cursor.close()

            self.authenticated = False
            self.seller_id = None
            return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            print("ERROR: Can not execute the given command.")
            print(e)
            return False, CMD_EXECUTION_FAILED
          


    """
        Quits from program.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Remember to sign authenticated user out first.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def quit(self, seller):
        # TODO: implement this function
        return False, CMD_EXECUTION_FAILED


    """
        Retrieves all available plans and prints them.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print available plans and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        #|Name|Max Sessions|Max Stocks Per Product
        1|Basic|2|4
        2|Advanced|4|8
        3|Premium|6|12
    """
    def show_plans(self):
        # TODO: implement this function
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subscription_plans")
            plans = cursor.fetchall()
            cursor.close()

            print("#|Name|Max Sessions|Max Stocks Per Product")
            for plan in plans:
                print(str(plan[0]) + "|" + plan[1] + "|" + str(plan[2]) + "|" + str(plan[3]))
            return True, CMD_EXECUTION_SUCCESS

        except Exception as e:
            print(e)
            return False, CMD_EXECUTION_FAILED
    
    def show_subscription(self, seller):
        # TODO: implement this function
        # bitmedi
        try:
            

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_subscription WHERE seller_id = %s", (seller,))
            subscription = cursor.fetchone()
            cursor.close()

            plan_id = subscription[3]

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subscription_plans WHERE plan_id = %s", (plan_id,))
            subscription = cursor.fetchone()
            cursor.close()


            print("#|Name|Max Sessions|Max Stocks Per Product")
            print(str(subscription[0]) + "|" + subscription[1] + "|" + str(subscription[2]) + "|" + str(subscription[3]))
            return True, CMD_EXECUTION_SUCCESS
        
        except Exception as e:
            print(e)
            return False, CMD_EXECUTION_FAILED
    
    
    """
        Change stock count of a product.
        - Return type is a tuple, 1st element is a seller object and 2nd element is the response message from messages.py.
        - If target product does not exist on the database, return tuple (False, PRODUCT_NOT_FOUND).
        - If target stock count > current plan's max_stock_per_product, return tuple (False, QUOTA_LIMIT_REACHED).
        - If the operation is successful, commit changes and return tuple (seller, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def change_stock(self, seller, product_id, change_amount):
        # TODO: implement this function
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_stocks WHERE product_id = %s", (product_id,))
            seller_stock = cursor.fetchone()
            cursor.close()

           

            if seller_stock is None:
                return False, PRODUCT_NOT_FOUND
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_subscription WHERE seller_id = %s", (seller,))
            seller_subscription = cursor.fetchone()
            cursor.close()
            plan_id = seller_subscription[3]
            

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subscription_plans WHERE plan_id = %s", (plan_id,))
            subscription_plan = cursor.fetchone()
            cursor.close()
            max_stock_per_product = subscription_plan[3]
           

            if seller_stock[2] + change_amount > max_stock_per_product:
                return False, QUOTA_LIMIT_REACHED
            if seller_stock[2] + change_amount < 0:
                return False, QUOTA_LIMIT_REACHED

            
            cursor = self.conn.cursor()
            cursor.execute("UPDATE seller_stocks SET stock_count = stock_count + %s WHERE product_id = %s and seller_id = %s", (change_amount, product_id, seller))
            self.conn.commit()
            cursor.close()
            print(CMD_EXECUTION_SUCCESS)
            return seller, CMD_EXECUTION_SUCCESS
            
           
        

        
        except Exception as e:
            print(e)
            return False, CMD_EXECUTION_FAILED
       


    """
        Retrieves authenticated seller's remaining quota for stocks and prints it. 
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print the authenticated seller's quota and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).

        If the seller is subscribed to a plan with max_stock_per_product = 12 and
        the current stock for product 92bf5d2084dfbcb57d9db7838bac5cd0 is 10, then output should be like:
        
        Product Id|Remaining Quota
        92bf5d2084dfbcb57d9db7838bac5cd0|2

        If the seller does not have a stock, print 'Quota limit is not activated yet.'
    """
    def show_quota(self, seller):
        # TODO: implement this function
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_subscription WHERE seller_id = %s", (seller,))
            seller_subscription = cursor.fetchone()
            cursor.close()
            plan_id = seller_subscription[3]

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subscription_plans WHERE plan_id = %s", (plan_id,))
            subscription_plan = cursor.fetchone()
            cursor.close()
            max_stock_per_product = subscription_plan[3]

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_stocks WHERE seller_id = %s", (seller,))
            seller_stocks = cursor.fetchall()
            cursor.close()
            if len(seller_stocks) == 0:
                print("Quota limit is not activated yet.")
                return True, QUOTA_INACTIVE
            print("Product Id|Remaining Quota")
            for stock in seller_stocks:
                print(stock[1] + "|" + str(max_stock_per_product - stock[2]))
            return True, CMD_EXECUTION_SUCCESS
        
        except Exception as e:
            print(e)
            return False, CMD_EXECUTION_FAILED
        

    """
        Subscribe authenticated seller to new plan.
        - Return type is a tuple, 1st element is a seller object and 2nd element is the response message from messages.py.
        - If target plan does not exist on the database, return tuple (None, PRODUCT_NOT_FOUND).
        - If the new plan's max_parallel_sessions < current plan's max_parallel_sessions, return tuple (None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE).
        - If the operation is successful, commit changes and return tuple (seller, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (None, CMD_EXECUTION_FAILED).
    """
    def subscribe(self, seller, plan_id):
        # TODO: implement this function
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subscription_plans WHERE plan_id = %s", (plan_id,))
            subscription_plan = cursor.fetchone()
            cursor.close()
            if subscription_plan is None:
                return None, PRODUCT_NOT_FOUND
            
            new_plan_max_parallel_sessions = subscription_plan[2]

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_subscription WHERE seller_id = %s", (seller,))
            seller_subscription = cursor.fetchone()
            cursor.close()
            old_plan_id = seller_subscription[3]

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM subscription_plans WHERE plan_id = %s", (old_plan_id,))
            old_subscription_plan = cursor.fetchone()
            cursor.close()
            old_plan_max_parallel_sessions = old_subscription_plan[2]

            if new_plan_max_parallel_sessions < old_plan_max_parallel_sessions:
                return None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE

            cursor = self.conn.cursor()
            cursor.execute("UPDATE seller_subscription SET plan_id = %s WHERE seller_id = %s", (plan_id, seller))
            self.conn.commit()
            cursor.close()
            return seller, CMD_EXECUTION_SUCCESS
        except Exception as e:
            print(e)
            return None, CMD_EXECUTION_FAILED

    """
        Change stock amounts for multiple distinct products.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If everything is OK and the operation is successful, return (True, CMD_EXECUTION_SUCCESS).
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any one of the product ids is incorrect; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
        - If any one of the products is not in the stock; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def ship(self, seller, product_ids):
        # TODO: implement this function
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM seller_stocks WHERE seller_id = %s", (seller,))
            seller_stocks = cursor.fetchall()
            cursor.close()

           


            for product_id in product_ids:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM seller_stocks WHERE product_id = %s and seller_id = %s", (product_id, seller))
                seller_stock = cursor.fetchone()
                cursor.close()
                if seller_stock is None:
                    return False, CMD_EXECUTION_FAILED
                
                if seller_stock[2] == 0:
                    return False, CMD_EXECUTION_FAILED
                
            for product_id in product_ids: 
                cursor = self.conn.cursor()
                cursor.execute("UPDATE seller_stocks SET stock_count = stock_count - 1 WHERE seller_id = %s AND product_id = %s", (seller, product_id))
                self.conn.commit()
                cursor.close()
            return True, CMD_EXECUTION_SUCCESS
        
        except Exception as e:
            print(e)
            return False, CMD_EXECUTION_FAILED
      
    

    """
        Retrieves the gross income per product category for every month.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print the results and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        Gross Income|Year|Month
        123.45|2018|1
        67.8|2018|2
    """
    def calc_gross(self, seller):
        # TODO: implement this function
        return False, CMD_EXECUTION_FAILED

    """
        Retrieves items on the customer's shopping cart
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print items on the cart and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        Seller Id|Product Id|Amount
        dd7ddc04e1b6c2c614352b383efe2d36|e5f2d52b802189ee658865ca93d83a8f|2
        5b51032eddd242adc84c38acab88f23d|c777355d18b72b67abbeef9df44fd0fd|3
        df560393f3a51e74553ab94004ba5c87|ac6c3623068f30de03045865e4e10089|1
    """
    def show_cart(self, customer_id):
        # TODO: implement this function
        return False, CMD_EXECUTION_FAILED
        
    """
        Change count of items in shopping cart
        - Return type is a tuple, 1st element is a seller object and 2nd element is the response message from messages.py.
        - If customer does not exist on the database, return tuple (False, CUSTOMER_NOT_FOUND).
        - If target product does not exist on the database, return tuple (False, PRODUCT_NOT_FOUND).
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
        - Consider stocks of sellers when you add items to the cart.
    """
    def change_cart(self, customer_id, product_id, seller_id, change_amount):
        # TODO: implement this function
        return False, CMD_EXECUTION_FAILED
    
    """
        Purchases items on the cart
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Actions:
        - Change stocks on seller_stocks table
        - Remove entries from customer_carts table
        - Add entries to order_items table
        - Add single entry to order table
    """
    def purchase_cart(self, customer_id):
        # TODO: implement this function
        return False, CMD_EXECUTION_FAILED
