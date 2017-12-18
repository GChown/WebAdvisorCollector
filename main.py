from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from src.navigator import Navigator
from selenium.common.exceptions import ElementNotVisibleException
import configparser
import datetime


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    username = config['DEFAULT']['username']
    password = config['DEFAULT']['password']
    baseurl = config['DEFAULT']['baseurl']

    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
    driver.get(baseurl)

    navigator = Navigator(driver)

    # Login
    navigator.click('/html/body/div/div[1]/div[1]/div/ul/li[3]/a/span')

    # Username
    navigator.fill('//*[@id="USER_NAME"]', username)
    #Password
    navigator.fill('//*[@id="CURR_PWD"]', password)

    # Log In
    navigator.click('/html/body/div/div[2]/div[4]/div[5]/form/div[2]/input')

    # Students
    navigator.click('//*[@id="mainMenu"]/a')

    # Search for Sections
    navigator.click('//*[@id="bodyForm"]/div[3]/div[1]/ul[4]/li[1]/a')

    # Select box HTML input
    termName = '2017 Winter'
    navigator.select('//*[@id="VAR1"]', termName)

    # For debug: only select courses in computer science
    subject = 'Computer Science'
    navigator.select('//*[@id="LIST_VAR1_1"]', subject)

    # Submit
    navigator.click('//*[@id="bodyForm"]/div[4]/form/div/input')

    insertCoursesQuery = "INSERT INTO courses(course_id, title, term, subject, courseLevel, capacity, available, " \
                         "credits, description, startDate, endDate, academicLevel, detailMeetingInfo, " \
                         "instructionalMethod, prerequisites) VALUES "

    insertLecturersQuery = "INSERT INTO lecturer(name, emailAddress) VALUES "

    insertLecturerJoinCoursesQuery = "INSERT INTO lecturer_course(lecturer_id, course_id) VALUES "

    insertCourseJoinPrerequisiteQuery = "INSERT INTO course_course(course_id1, course_id_prerequisite) VALUES "

    def parseXpathToQuery(xpath, addquotes = True):
        pathvalue = navigator.query(xpath).get_attribute('innerHTML')
        pathvalue = pathvalue.replace('"', '\\"')
        if addquotes:
            return '"' + pathvalue + '"'
        else:
            return pathvalue

    small_sample = 5
    medium_sample = 15
    large_sample = 100
    production_sample = 2000
    for i in range(1, small_sample):
        insertCourseQuery = ''
        try:
            # Click link to open info
            link = navigator.click('//*[@id="SEC_SHORT_TITLE_' + str(i) + '"]')

            available = capacity = '0'

            # String like "24 / 50"
            availableOverCapacity = parseXpathToQuery('//*[@id="LIST_VAR5_' + str(i) + '"]', False).split(' / ')
            if len(availableOverCapacity) == 2:
                available = '"' + availableOverCapacity[0] + '"'
                capacity = '"' + availableOverCapacity[1] + '"'

            # Switch to new tab
            driver.switch_to.window(driver.window_handles[1])

            title = parseXpathToQuery('//*[@id="VAR1"]')
            course_id = parseXpathToQuery('//*[@id="VAR2"]')
            description = parseXpathToQuery('//*[@id="VAR3"]')
            credits = parseXpathToQuery('//*[@id="VAR4"]')

            startDateString = parseXpathToQuery('//*[@id="VAR6"]', False)
            endDateString = parseXpathToQuery('//*[@id="VAR7"]', False)

            # UNIX timestamps
            startDate = str(datetime.datetime.strptime(startDateString, '%d %B %Y').strftime("%s"))
            endDate = str(datetime.datetime.strptime(endDateString, '%d %B %Y').strftime("%s"))

            academicLevel = parseXpathToQuery('//*[@id="VAR8"]')
            detailMeetingInfo = parseXpathToQuery('//*[@id="LIST_VAR12_1"]')
            instructionalMethod = parseXpathToQuery('//*[@id="LIST_VAR11_1"]')

            profName = parseXpathToQuery('//*[@id="LIST_VAR7_1"]')
            profEmail = parseXpathToQuery('//*[@id="LIST_VAR10_1"]')

            # Something like '#take cosc-2006el cosc-3707el;'
            prerequisites = parseXpathToQuery('//*[@id="VAR_LIST1_1"]')

            insertThisCourseQuery = '(' + ','.join([course_id, title, '"' + termName + '"', '"' + subject + '"',
                                                    '"courseLevel"', capacity, available, credits, description,
                                                    startDate, endDate, '"academicLevel"', detailMeetingInfo,
                                                    instructionalMethod, prerequisites]) + ')'

            insertThisLecturerQuery = '(' + ','.join([profName, profEmail]) + ')'

            # Need to get lecturer ID from name for this join
            insertThisLecturerJoinThisCourseQuery = '(' + ','.join(
                ['(SELECT lecturer_id FROM lecturer WHERE name=' + profName + ')',
                 course_id]) + ')'

            insertCoursesQuery = ','.join([insertCoursesQuery, insertThisCourseQuery]) + ';'

            insertLecturersQuery = ','.join([insertLecturersQuery, insertThisLecturerQuery]) + ';'

            insertLecturerJoinCoursesQuery = ','.join(
                [insertLecturerJoinCoursesQuery, insertThisLecturerJoinThisCourseQuery]) + ' ON DUPLICATE SET name=name;'

            # Click Close Window button
            navigator.click('//*[@id="bodyForm"]/div[4]/form/div/input')
        # If we hit ElementNotVisible it's likely because we tried to click a link that's not there,
        # so we know we've got the last of the table rows
        except ElementNotVisibleException:
            break
        except Exception:
            print('Exception received')
        finally:
            driver.switch_to.window(driver.window_handles[0])

    print(" --- INSERT COURSES QUERY --- ")
    print(insertCoursesQuery)
    print(" --- INSERT LECTURERS QUERY --- ")
    print(insertLecturersQuery)
    print(" --- JOIN LECTURER - COURSES QUERY --- ")
    print(insertLecturerJoinCoursesQuery)

    driver.quit()
