from bs4 import BeautifulSoup
import requests
from lxml import etree
import re


def get_souped_page(page_url):
    '''
    In order not to be blocked for scraping its import to request pages with
    some settings to look more like an actual browser.

    this function takes a page_url from https://www.transfermarkt.com and returns the
    souped page
    '''
    headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

    pageTree = requests.get(page_url, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')

    return(pageSoup)



def remove_youth(team_string):
    '''
    There are many variations of each club name to identify each squad within
    that club.

    this function takes a team string and returns the team string without youth
    variations
    '''
    team_string = team_string.replace("U15", "")
    team_string = team_string.replace("U16", "")
    team_string = team_string.replace("U17", "")
    team_string = team_string.replace("U18", "")
    team_string = team_string.replace("U19", "")
    team_string = team_string.replace("U20", "")
    team_string = team_string.replace("U21", "")
    team_string = team_string.replace("U22", "")
    team_string = team_string.replace("U23", "")
    team_string = team_string.replace("u15", "")
    team_string = team_string.replace("u16", "")
    team_string = team_string.replace("u17", "")
    team_string = team_string.replace("u18", "")
    team_string = team_string.replace("u19", "")
    team_string = team_string.replace("u20", "")
    team_string = team_string.replace("u21", "")
    team_string = team_string.replace("u22", "")
    team_string = team_string.replace("u23", "")
    team_string = team_string.replace("II", "")
    team_string = team_string.replace("ii", "")
    team_string = team_string.replace("Youth", "")
    team_string = team_string.replace("jugend", "")
    team_string = team_string.replace("Academy", "")
    team_string = team_string.replace("Academia", "")
    team_string = team_string.replace("B \(liq.\)", "")
    team_string = team_string.replace("C \(liq.\)", "")
    team_string = team_string.strip()
    return(team_string)


def calculate_age_at_transfer(born, transfer_date):
    '''
    Calculate the age between the date of transfer and the date of birth of the
    player
    '''
    return transfer_date.year - born.year - ((transfer_date.month, transfer_date.day) < (born.month, born.day))


def calculate_age(born, competition_start):
    '''
    Calculate the age between the start date of a competition and the date of birth of the
    player
    '''
    return(competition_start.year - born.year - ((competition_start.month, competition_start.day) < (born.month, born.day)))


def stringify_children(node):
    '''
    a helper to convert the market value chart data into strings
    '''
    s = node.text
    if s is None:
        s = ''
    for child in node:
        s += etree.tostring(child, encoding='unicode')
    return s


def month_to_number(month_string):
    '''
    a helper to change month abbreviations to month numbers
    '''
    month_map = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
    return month_map[month_string]
