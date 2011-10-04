import doctest
import unittest2 as unittest

DOCFILES = [
    # test attachment first, will be used in databaseUtil 
    ('controller/attachmentUtil.txt'),
    ('controller/databaseUtil.txt'),
    ('controller/mailParserUtil.txt'),
    ('mail_to_sql.txt'),
]

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

def test_suite():
    suite = unittest.TestSuite()

    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=optionflags,
        )
        for docfile in DOCFILES
    ])
    
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')