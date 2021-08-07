import requests


class frappeAPI:
    '''
    This class is used for interacting with the frappe api.
    '''

    @staticmethod
    def add_counters(booklist : list):
        '''
        Args:
            - booklist (list) - the list of books where you want to add counter column(s)
        
        TODO: optimize (could use a dict)
        '''

        bookid_set = set()
        books = []

        if not isinstance(booklist, list):
            raise Exception("Please provide booklist (list) where you want to add counter column(s).")

        after_len = 0
        for book in booklist:
            before_len = after_len
            bookid_set.add(book["bookID"])
            after_len = len(bookid_set)

            if after_len > before_len:
                book["available_quantity"] = 1
                book["times_rented"] = 0
                books.append(book)
            else:
                for b in books:
                    if b["bookID"] == book["bookID"]:
                        b["available_quantity"] += 1

        return books


    @staticmethod
    def get_data(
        number_of_books : int, 
        authors : str="", 
        title : str="", 
        publisher : str="", 
        isbn : str=""
        ):

        '''
        Required Args:
            - number_of_books (int) - the number of books you want to fetch for the query
        '''

        book_list = []

        if not isinstance(number_of_books, int):
            raise Exception("Please provide number_of_books (int) you want to to fetch")

        page = 1
        while number_of_books > 0:
            try:
                response = requests.get(
                    f"https://frappe.io/api/method/frappe-library?title={title}&authors={authors}&publisher={publisher}&isbn={isbn}&page={page}"
                ).json()
            except Exception:
                print("Exception, API response was: ", response)
                break

            data = response.get("message")

            if data and isinstance(data, list):
                if len(data) == 20 and number_of_books > 20:
                    number_of_books = number_of_books - 20 
                    page = page + 1
                else:
                    # if numberofbooks > data, give then full data (whatever is available) else give the requested amount
                    data = data[:number_of_books]
                    number_of_books = 0

                book_list.extend(data)
            else:
                break

        return len(book_list), frappeAPI.add_counters(book_list)

