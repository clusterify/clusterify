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