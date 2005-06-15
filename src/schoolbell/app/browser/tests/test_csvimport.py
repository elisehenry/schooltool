#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2004 Shuttleworth Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Unit tests for schoolbell.app.browser.csvimport

$Id$
"""

import unittest

from zope.testing import doctest
from zope.publisher.browser import TestRequest
from zope.i18n import translate

from schoolbell.app.browser.tests.setup import setUp, tearDown

__metaclass__ = type


def doctest_BaseCSVImporter():
    r"""Test for BaseCSVImporter

    Set up

        >>> from schoolbell.app.browser.csvimport import BaseCSVImporter
        >>> importer = BaseCSVImporter(None)

    Subclasses need to define the createAndAdd method

        >>> importer.createAndAdd(None)
        Traceback (most recent call last):
        ...
        NotImplementedError: Please override this method in subclasses

    When given a list of CSV rows parseCSVRows should return a list of lists

        >>> data = ["one, two, three", "four, five, six"]
        >>> importer.parseCSVRows(data)
        [['one', 'two', 'three'], ['four', 'five', 'six']]

    parseCSVRows can also set errors should they occur

        >>> data = ["one, \xff"]
        >>> importer.charset = 'UTF-8'
        >>> importer.parseCSVRows(data)
        >>> translate(importer.errors.generic[0])
        u'Conversion to unicode failed in line 1'

    Moving on, importFromCSV calls createAndAdd which we have not defined

        >>> csvdata = "one, two, three\nfour, five, six"
        >>> importer.importFromCSV(csvdata)
        Traceback (most recent call last):
        ...
        NotImplementedError: Please override this method in subclasses

    We need to make a subclass to test this properly

        >>> class TestCSVImporter(BaseCSVImporter):
        ...     def __init__(self):
        ...         BaseCSVImporter.__init__(self, None, 'UTF-8')
        ...     def createAndAdd(self, data, True):
        ...         pass

        >>> myimporter = TestCSVImporter()

    importFromCSV just returns True if everything goes well

        >>> myimporter.importFromCSV(csvdata)
        True

    False is returned if there are errors

        >>> myimporter.importFromCSV("one, two\nthree, \xff")
        False
        >>> translate(myimporter.errors.generic[0])
        u'Conversion to unicode failed in line 2'

    """


def doctest_GroupCSVImporter():
    r"""Tests for GroupCSVImporter.

    Create a group container and an importer

        >>> from schoolbell.app.browser.csvimport import GroupCSVImporter
        >>> from schoolbell.app.app import GroupContainer
        >>> container = GroupContainer()
        >>> importer = GroupCSVImporter(container, None)

    Import some sample data

        >>> csvdata='''Group 1, Group 1 Description
        ... Group2
        ... Group3, Group 3 Description, Some extra data'''
        >>> importer.importFromCSV(csvdata)
        True

    Check that the groups exist

        >>> [group for group in container]
        [u'group-1', u'group2', u'group3']

    Check that descriptions were imported properly

        >>> [group.description for group in container.values()]
        ['Group 1 Description', '', 'Group 3 Description']

    """

def doctest_ResourceCSVImporter():
    r"""Tests for ResourceCSVImporter.

    Create a resource container and an importer

        >>> from schoolbell.app.browser.csvimport import ResourceCSVImporter
        >>> from schoolbell.app.app import ResourceContainer
        >>> container = ResourceContainer()
        >>> importer = ResourceCSVImporter(container, None)

    Import some sample data

        >>> csvdata='''Resource 1, Resource 1 Description
        ... Resource2
        ... Resource3, Resource 3 Description, location
        ... Resource4, , location'''
        >>> importer.importFromCSV(csvdata)
        True

    Check that the resources exist

        >>> [resource for resource in container]
        [u'resource-1', u'resource2', u'resource3', u'resource4']

    Check that descriptions were imported properly

        >>> [resource.description for resource in container.values()]
        ['Resource 1 Description', '', 'Resource 3 Description', '']
        >>> [resource.isLocation for resource in container.values()]
        [False, False, True, True]

    """

def doctest_GroupCSVImportView():
    r"""Tests for GroupCSVImportView

    We'll create a group csv import view

        >>> from schoolbell.app.browser.csvimport import GroupCSVImportView
        >>> from schoolbell.app.app import GroupContainer
        >>> from zope.publisher.browser import TestRequest
        >>> container = GroupContainer()
        >>> request = TestRequest()

    Now we'll try a text import.  Note that the description is not required

        >>> request.form = {'csvtext' : "A Group, The best Group\nAnother Group",
        ...                 'charset' : 'UTF-8',
        ...                 'UPDATE_SUBMIT': 1}
        >>> view = GroupCSVImportView(container, request)
        >>> view.update()
        >>> [group for group in container]
        [u'a-group', u'another-group']

    If no data is provided, we naturally get an error

        >>> request.form = {'charset' : 'UTF-8', 'UPDATE_SUBMIT': 1}
        >>> view.update()
        >>> view.errors
        [u'No data provided']

    We also get an error if a line starts with a comma (no title)

        >>> request.form = {'csvtext' : ", No title provided here",
        ...                 'charset' : 'UTF-8',
        ...                 'UPDATE_SUBMIT': 1}
        >>> view = GroupCSVImportView(container, request)
        >>> view.update()
        >>> view.errors
        [u'Failed to import CSV text', u'Titles may not be empty']

    """

def doctest_ResourceCSVImportView():
    r"""
    We'll create a resource csv import view

        >>> from schoolbell.app.browser.csvimport import ResourceCSVImportView
        >>> from schoolbell.app.app import ResourceContainer
        >>> from zope.publisher.browser import TestRequest
        >>> container = ResourceContainer()
        >>> request = TestRequest()

    Now we'll try a text import.  Note that the description is not required

        >>> request.form = {'csvtext' : "A Resource, The best Resource\nAnother Resource",
        ...                 'charset' : 'UTF-8',
        ...                 'UPDATE_SUBMIT': 1}
        >>> view = ResourceCSVImportView(container, request)
        >>> view.update()
        >>> [resource for resource in container]
        [u'a-resource', u'another-resource']

    If no data is provided, we naturally get an error

        >>> request.form = {'charset' : 'UTF-8', 'UPDATE_SUBMIT': 1}
        >>> view.update()
        >>> view.errors
        [u'No data provided']

    We also get an error if a line starts with a comma (no title)

        >>> request.form = {'csvtext' : ", No title provided here",
        ...                 'charset' : 'UTF-8',
        ...                 'UPDATE_SUBMIT': 1}
        >>> view = ResourceCSVImportView(container, request)
        >>> view.update()
        >>> view.errors
        [u'Failed to import CSV text', u'Titles may not be empty']

    """

def doctest_ImportErrorCollection():
    r"""
    Make the class

        >>> from schoolbell.app.browser.csvimport import ImportErrorCollection
        >>> errors = ImportErrorCollection()
        >>> errors
        <ImportErrorCollection {'generic': [], 'fields': []}>

    anyErrors returns True if there are errors and False if not

        >>> errors.anyErrors()
        False
        >>> errors.fields.append('A Sample Error Message')
        >>> errors.anyErrors()
        True

    """

def doctest_PersonCSVImporter():
    r"""Tests for PersonCSVImporter.

    Create a person container and an importer

        >>> from schoolbell.app.browser.csvimport import PersonCSVImporter
        >>> from schoolbell.app.app import PersonContainer
        >>> container = PersonContainer()
        >>> importer = PersonCSVImporter(container, None)

    Import a user and verify that it worked

        >>> importer.createAndAdd([u'joe', u'Joe Smith'], False)
        >>> [p for p in container]
        [u'joe']

    Import a user with a password and verify it

        >>> importer.createAndAdd([u'jdoe', u'John Doe', u'monkey'], False)
        >>> container['jdoe'].checkPassword('monkey')
        True

    Some basic data validation exists.  Note that the errors are cumulative
    between calls on an instance.

        >>> importer.createAndAdd([], False)
        >>> importer.errors.fields
        [u'Insufficient data provided.']
        >>> importer.createAndAdd([u'', u'Jim Smith'], False)
        >>> importer.errors.fields
        [u'Insufficient data provided.', u'username may not be empty']
        >>> importer.createAndAdd([u'user', u''], False)
        >>> importer.errors.fields
        [u'Insufficient data provided.', u'username may not be empty', u'fullname may not be empty']

    Let's clear the errors and review the contents of the container

        >>> importer.errors.fields = []
        >>> [p for p in container]
        [u'jdoe', u'joe']

    Now we'll try to add another 'jdoe' username.  In this case the error
    message contains a translated variable, so we need zope.i18n.translate to
    properly demonstrate it.

        >>> from zope.i18n import translate
        >>> importer.createAndAdd([u'jdoe', u'Jim Doe'], False)
        >>> [translate(error) for error in importer.errors.fields]
        [u'Duplicate username: jdoe, Jim Doe']

    """

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(setUp=setUp, tearDown=tearDown,
                                       optionflags=doctest.ELLIPSIS|
                                                   doctest.REPORT_NDIFF))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
