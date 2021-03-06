from plone.app.testing import PLONE_FIXTURE, PLONE_FUNCTIONAL_TESTING, PLONE_INTEGRATION_TESTING
from plone.app.testing import PloneSandboxLayer, FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig
from plone.testing.z2 import Browser
from zope.testbrowser.browser import controlFactory
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD, setRoles, login
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD


class CollectiveListingviews(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.listingviews
        xmlconfig.file('configure.zcml',
                       collective.listingviews,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        applyProfile(portal, 'collective.listingviews:default')

class BrowserIntegrationTesting(IntegrationTesting):

    def setUpEnvironment(self, portal):
        super(BrowserIntegrationTesting, self).setUpEnvironment(portal)
        portal = self['portal']

        browser = Browser(portal)
        portalURL = portal.absolute_url()
        browser.open(portal.absolute_url()+'/@@listingviews_controlpanel')

        browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
        browser.getControl(name='submit').click()
        self['manager'] = browser

        # create dummy content

        browser.getLink('Home').click()
        browser.getLink('Folder').click()
        browser.getControl('Title').value = 'folder1'
        browser.getControl('Save').click()

        #Add an item
        browser.getLink('Page').click()
        browser.getControl('Title').value = 'item1'
        browser.getControl('Save').click()
        browser.getLink('Publish').click()


        browser.getLink('folder1').click()

        browser.getLink('Collection').click()
        browser.getControl('Title', index=0).value = "collection1"
        browser.getControl('Location', index=0).click()
        form = browser.getControl('Location', index=0).mech_form
        form.new_control('text','query.i:records', {'value':'path'})
        form.new_control('text','query.o:records', {'value':'plone.app.querystring.operation.string.relativePath'})
        form.new_control('text','query.v:records', {'value':'..'})
        browser.getControl('Save').click()

        browser.getLink('Home').click()


    def getFormFromControl(self, control):
        browser = control.browser
        index = 0
        while True:
            try:
                form = browser.getForm(index=index)
            except:
                return None
            if form.mech_form == control.mech_form:
                return form
            else:
                index += 1
                continue

    def getControls(self, form):
        if getattr(form, 'mech_control', None) is not None or getattr(form, 'mech_item', None) is not None:
            return getattr(form, 'controls', [])
        else:
            #assume its a form
            return [controlFactory(c, form.mech_form, form.browser) for c in form.mech_form.controls]

    def isSameControl(self, subcontrol, control):
        try:
            if subcontrol.mech_control == control.mech_control:
                return True
        except:
            pass
        try:
            if subcontrol.mech_item == control.mech_item:
                return True
        except:
            pass
        return False



    def getControlParents(self, control, parents=[]):
        if not parents:
            parents = [self.getFormFromControl(control)]
        parent = parents[-1]
        for subcontrol in self.getControls(parent):
            if self.isSameControl(subcontrol, control):
                return parents
            new_parents = self.getControlParents(control, parents+[subcontrol])
            if new_parents:
                return new_parents
        return None


    def setInAndOut(self, browser, labels, index=None):
        main_control = browser.getControl(labels[0], index=index).control
        #parents = self.getControlParents(main_control)
        #form = self.getFormFromControl(main_control)
        #import pdb; pdb.set_trace()

        name = main_control.name.rstrip('.to').rstrip('.from')
        index = 0
        for label in labels:
            value = None
            for item in main_control.controls:
                if item.mech_item.get_labels()[0]._text == label:
                    value = item.optionValue
                    break
            if not value:
                raise Exception("No item found with label '%s' in %s"%(label, main_control))
            main_control.mech_form.new_control('text','%s:list'%name, {'value':value}, index=index)
            index += 1


    def errorlog(self):
        from Products.CMFCore.utils import getToolByName
        portal = self['portal']
        errorLog = getToolByName(portal, 'error_log')
        print errorLog.getLogEntries()[-1]['tb_text']



COLLECTIVE_LISTINGVIEWS_FIXTURE = CollectiveListingviews()
COLLECTIVE_LISTINGVIEWS_INTEGRATION_TESTING = \
    BrowserIntegrationTesting(bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE, ),
                            name="CollectiveListingviews:Integration")

FIXTURE = CollectiveListingviews()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE,),
    name='example.conference:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_LISTINGVIEWS_FIXTURE,),
    name='example.conference:Functional',
    )