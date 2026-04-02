'''
Important!
Enter your full name (as it appears on Canvas) and NetID.  
If you are working in a group (maximum of 3 members), include the full names and NetIDs of all your partners.  
If you're working alone, enter `None` for the partner fields.
'''

'''
Project: MP4
Student 1: Ebenezer Idowu Jr, eaidowu
Student 2: Praneel,  nakkina

'''

# Add additional imports if needed

from collections import deque
import os
import time
import requests
import pandas as pd
from io import StringIO
from selenium.webdriver.common.by import By

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ 
        Leave this method as is! It will be over-written the child classes
        Each child class should perform the following:
            Record the node value in self.order AND return its children
            parameter: node
            return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited = set()
        self.order = []
        # 2. start recursive search by calling dfs_visit
        self.dfs_visit(node)

    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        # 3. call self.visit_and_get_children(node) to get the children
        curr_node_children = self.visit_and_get_children(node)
        # 4. in a loop, call dfs_visit on each of the children
        for child in curr_node_children:
            self.dfs_visit(child)

    def bfs_search(self, node):
        #clear out visited and order list
        self.order = []
        self.visited = set()
        
        bfs_queue = deque()
        #visit starting node and add to queue
        bfs_queue.append(node)
        
        while len(bfs_queue) != 0:
            curr_node = bfs_queue.popleft()
            self.visited.add(curr_node)
            neighbors = self.visit_and_get_children(curr_node)
            for neigh in neighbors:
                if neigh not in self.visited and neigh not in bfs_queue:
                    bfs_queue.append(neigh)
                    
        

class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def visit_and_get_children(self, node):
        # record the node value in self.order
        self.order.append(node)
        children = []
        
        # use `self.df` to determine what children the node has and append them-DONE
        for node, has_edge in self.df.loc[node].items():
            if has_edge==1:
                children.append(node)

        return children


class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()

    def visit_and_get_children(self, node):
         # open the file in file_nodes, then parse the value and children
            
        #open file raw
        with open("file_nodes/" + node, "r") as file:
            curr_file = file.readlines()

            #remove newline characters
            clean_file = [line.strip() for line in curr_file]

            #separate node and chilren
            curr_node = clean_file[0]
            curr_children = clean_file[1].split(",")

            # record value in self.order
            self.order.append(curr_node)
            return curr_children
        
   
        
    def concat_order(self):
        # TODO: return joined string of self.order
        #iterate thru self.order, add all to a string
        all_nodes = ""
        num_nodes = len(self.order)
        for i in range(num_nodes):
            curr_node = str(self.order[i])
            all_nodes += curr_node
           
        return all_nodes
    


class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.tables = []

    def visit_and_get_children(self, node):
        #redundant check for already visited
        # if node in self.visited:
        #     return []
        
        the_driver = self.driver
        the_driver.get(node)
        
        # record node in self.order
            #get the node AS A URL (debug fix)
        self.order.append(node)
        
        # fetch the page, parse HTML table into pandas, store it
        tables = pd.read_html(StringIO(the_driver.page_source), attrs = {"id":"locations-table"})
        
        #get table for the curr page
        if len(tables) > 0:
            curr_table = tables[0]
            self.tables.append(curr_table)
        
        #return list of links (<a> tags)-DONE
        child_links = []
        links = the_driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            link_url = link.get_attribute("href")
            if link_url is not None and link_url not in self.visited:
                child_links.append(link_url)
        #print(f"child_links: {child_links}")
        return child_links
        
        
        
    def table(self):
        # TODO: return combined DataFrame-DONE
        all_tables = self.tables
        all_dframes = []
        if not self.tables:
            return pd.DataFrame()
            
        return pd.concat(self.tables, ignore_index=True)
        
    
    
def get_password(travellog):
    """
    Given a DataFrame-like object with a 'clue' column,
    combine values into a password string.
    """
    # build string from travellog['clue']
    gen_password = ""
    clues = travellog['clue']
    for curr in clues:
        gen_password+=str(curr)
    return gen_password


def reveal_secrets(driver, url, travellog):
    """
    Automate secret-revealing:
    1. Generate clue/password
    2. Enter password into webpage
    3. Click buttons, wait for image
    4. Save image
    5. Return the location text
    """
    # TODO: implement using Selenium driver, retries, and requests-DONE

    #generate clue/password
    gen_password = get_password(travellog)

    #visit url with driver
    driver.get(url)

    #enter password into webpage
    pword_entry = driver.find_element(By.ID, "password-textbox")
    pword_entry.send_keys(gen_password)
    #click on go button
    go_button = driver.find_element(By.ID, "submit-button")
    go_button.click()

    #wclick view location and wait until loaded
    while True:
        try:
            location_btn = driver.find_element(By.ID,"location-button") 
            break
        except:
            time.sleep(1)

    location_btn.click()
    time.sleep(1)
    #save image: get and download image from page, write it to file
    #image_page = driver.page_source
    image = driver.find_element(By.ID, "image")
    image_url = image.get_attribute("src")
    image = requests.get(image_url) #download image
    with open('Current_Location.jpg', 'wb') as file:
        file.write(image.content)
    #return curr page location
    curr_location = driver.find_element(By.ID, "location").text
    return curr_location

        
        
            
        