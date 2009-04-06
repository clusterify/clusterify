"""
"The contents of this file are subject to the Common Public Attribution
License Version 1.0 (the "License"); you may not use this file except 
in compliance with the License. You may obtain a copy of the License at 
http://www.clusterify.com/files/CODE_LICENSE.txt. The License is based 
on the Mozilla Public License Version 1.1 but Sections 14 and 15 have 
been added to cover use of software over a computer network and provide 
for limited attribution for the Original Developer. In addition, Exhibit 
A has been modified to be consistent with Exhibit B.

Software distributed under the License is distributed on an "AS IS" basis, 
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
for the specific language governing rights and limitations under the 
License.

The Original Code is Clusterify.

The Initial Developer of the Original Code is "the Clusterify.com team", 
which is described at http://www.clusterify.com/about/. All portions of 
the code written by the Initial Developer are Copyright (c) the Initial 
Developer. All Rights Reserved.
"""

from projects.models import Project
from django.contrib.auth.models import User
from django.http import HttpResponse

from registration.models import Profile


# Dev utility function to populate the db with dummy objects
# TODO: remove this when DEBUG is false
def populate_projects(request):
	u = User.objects.create_user('moe', 'him@bar.com', 'blah')
	u.is_staff = True
	u.save()
	
	p = Profile(user=u)
	p.save()
	
	u2 = User.objects.create_user('john', 'lennon@thebeatles.com', 'blah')
	u2.is_staff = True
	u2.save()
	
	p = Profile(user=u2)
	p.save()
	
	project = Project(author=u, title="Project 1", description_markdown="Lorem ipsum.", score_proposed=131.0)
	project.save()
	project.set_tags("dtag1 dtag2 dtag3")
	
	project = Project(author=u, title="Project 2 -- completed", description_markdown="And dolor sit amet and stuff.", p_completed=True)
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	project = Project(author=u, title="Project 3", description_markdown="", score_proposed=131.3)
	project.save()
	project.set_tags("dtag1 dtag2 dtag3")
	
	project = Project(author=u, title="Project 4", description_markdown="", score_proposed=131.6)
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	project = Project(author=u, title="Project 5", description_markdown="", score_proposed=132.0)
	project.save()
	project.set_tags("dtag1 dtag2 dtag3")
	
	project = Project(author=u2, title="Project 6", description_markdown="", score_proposed=133.0)
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	project = Project(author=u2, title="Project 7", description_markdown="")
	project.save()
	project.set_tags("dtag1 dtag2 dtag3")
	
	project = Project(author=u2, title="Project 8", description_markdown="")
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	project = Project(author=u2, title="Project 9", description_markdown="")
	project.save()
	project.set_tags("dtag1 dtag2 dtag3")
	
	project = Project(author=u2, title="Project 10", description_markdown="")
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	project = Project(author=u2, title="Project 11", description_markdown="")
	project.save()
	project.set_tags("dtag1 dtag2 dtag3")
	
	project = Project(author=u2, title="Project 12", description_markdown="")
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	project = Project(author=u2, title="Project 13", description_markdown="")
	project.save()
	project.set_tags("dtag4 dtag5 dtag6")
	
	
	##########
	
	u = User.objects.create_user('billy', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('joe', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('elvis', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('tania', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('chloe', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('bilbo', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('frodo', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('randy', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('claire', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('homer', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('bart', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('lisa', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('maggy', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('caroline', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('bob', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('alice', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('charlie', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('eve', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	u = User.objects.create_user('kirk', 'lennon@thebeatles.com', 'blah')
	u.save()
	p = Profile(user=u, description_markdown="Une lentille optique est un morceau de materiau transparent, comme du verre, dont les surfaces sont en general spheriques ou cylindriques. Le terme lentille vient du mot latin designant la legumineuse du meme nom.")
	p.save()
	p.set_tags("cobol fortran punchcards vacuumtubes")
	
	return HttpResponse("Done.")