from django.db import models
from django.contrib.auth.models import User

#A phase represents the start of a payment context agreed upon in which
#certain users get a certain share of the earnings. When the shares agreement
#changes, a new phase begins. Then when another agreement occurs, yet another
#phase is started. So on and so forth...
class Phase(models.Model):
    num = models.IntegerField(default=0)
    startDate = models.DateField(default="", blank=True)
    
    def __str__(self):
        return str("{} : {}".format(self.num, self.startDate))

#This is a user profile that is linked to an authorized user account. This
#describes the user breifly and also stores the encrypted passphrase for login
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    passphraseData = models.TextField(max_length=1500)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    
    def __str__(self):
        return "{} : {} {}".format(self.user, self.firstName, self.lastName)

#A payout period is a part of a phase. It consists of a group of periods.
    #(See Period)
class PayoutPeriod(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, default="")
    num = models.IntegerField(default=0)
    notes = models.TextField(max_length=1000, default="", blank=True)
    paidOut = models.BooleanField(default=False, blank=True)
    membersPaid = models.TextField(max_length=1000, default="", blank=True)
    
    def __str__(self):
        return str("{}: Phase ({})".format(self.num,self.phase))
#A period is a time when a payout was recieved from the mining pool. It belongs
#to a group of other periods called a payout period
class Period(models.Model):
    payoutPeriod = models.ForeignKey(PayoutPeriod, on_delete=models.CASCADE, default="")
    num = models.IntegerField(default=0)
    date = models.DateTimeField()
    amount = models.FloatField(default="")
    
    def __str__(self):
        return "{} - {} - {} ZEC {}".format(self.num, self.date, self.amount, self.payoutPeriod)
#     hashratePercent = models.FloatField(default='')
