import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import webbrowser


def identity(x):
    return x

def list_transpose(list_of_pairs):
    """
    Takes a list of two-element lists and returns a two-element
    list of lists corresponding with the pairs.
    """

    for x in list_of_pairs:
        if len(x) != 2:
            for y in list_of_pairs:
                print(y)
            raise ValueError(
            f"""Need to input lists of length two.
            Check that the string sep cut all strings into two pieces. 
            Your list has this in it:
            {x}
            """
            )

    return list(map(list, zip(*list_of_pairs)))


def name_to_storage_path(name: str):
    """takes a name (like pitchfork) and returns the filepath ./data/name.html."""
    return os.path.join(".", "data", name + ".html")


class DataCleaner:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.path = name_to_storage_path(name)
        self.get_soup()

    def get_soup(self):
        """
        Small wrapper around urllib and BeautifulSoup. Takes a url
        and produces the soup object. Includes a header so that 
        http errors are less likely.

        For reproducibility, this will save and load an html file
        rather than pull the html again from the host. 
        If you really want to overwrite the saved html, then delete
        from the terminal.
        """

        if not os.path.exists(self.path):
            # then we need to create it.

            req = Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
            page = urlopen(req)
            self.soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")

            with open(self.path, "w+") as file:
                file.write(str(self.soup))
        else:
            # we just need to read the soup in.
            link = open(self.path)
            self.soup = BeautifulSoup(link.read(), "html.parser")

    def create_tags(self, html_tag, **kwargs):
        """
        Takes a soup object and returns a list of tag.texts from the
        specified html_tag.
        """
        self.strings = [tag.text for tag in self.soup.find_all(html_tag, **kwargs)]

    def split(self, sep):

        self.strings = [x.strip().split(sep, 1) for x in self.strings]

    def reorganize(self):
        """
        use this if the state comes out as 
        [artist_1, album_1, artist_2, album_2, ...].
        """
        self.artists, self.albums = [self.strings[::2], self.strings[1::2]]

    def apply(self, attr, func):
        """
        Applies the func to each element of self.attr once the state has been transposed.
        """
        
        setattr(self, attr, list(map(func, getattr(self, attr))))
        
    
    def extract_year_from_paren(self, attr, delim="()"):
        
        self.years = [s[s.rfind(delim[0]) + 1 : s.rfind(delim[1])].strip() for s in getattr(self, attr)]
        setattr(self, attr, )
        
    def trim(self, attr, chars, left=True, right=False):
        """
        Remove any of the characters in `char` from the left or right (or both).
        """
        if left:
            setattr(self, attr, [x.lstrip(chars) for x in getattr(self, attr)])
        if right:
            setattr(self, attr, [x.rstrip(chars) for x in getattr(self, attr)])

    def transpose(self):
        """ 
        Turns the state from a list of lists to a
        list of  two lists. 
        """

        self.artists, self.albums = list_transpose(self.strings)

    def create_df(self, rank_list):
        """ Takes the lists and produces a dataframe out of them."""

        self.df = pd.DataFrame({"artist": self.artists, "album": self.albums})

        self.df["rank"] = rank_list

        self.df["genre"] = None
        if hasattr(self, "years"):
            self.df["year"] = self.years
            
        self.df["reviewer"] = self.name
        self.df["reviewer_url"] = self.url
        

    def print_data(self):
        if hasattr(self, "albums"):
            for (artist, album) in zip(self.artists, self.albums):
                print([artist, album])
        else:
            for li in self.strings:
                print(li)
        if hasattr(self, "years"):
            for year in self.years:
                print(year)
                
        if hasattr(self, "df"):
            print(self.df)
            
    def view_page(self):
        webbrowser.open("file://" + os.path.abspath(self.path))
    
    def __len__(self):
        if hasattr(self, "artists"):
            return len(self.artists)
        elif hasattr(self, "strings"):
            return len(self.strings)
        else:
            return None
