from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib import messages
from deals.models import Deal
from deals.baseviews import DealListBaseView
from merchant.forms import DealForm
from merchant.mixins import MerchantMixin


class ManageDealsView(MerchantMixin, DealListBaseView):

    """Manage deals"""
    def get(self, request):
        """Renders a listing page for all deals that was created by a merchant
        """
        # context_data = Deal.objects.filter(
        #     advertiser=request.user.profile.merchant
        # )
        advertiser_id = request.user.profile.merchant.advertiser_ptr.id
        deals = Deal.objects.filter(advertiser=advertiser_id)
        # deals = Deal.objects.filter(
        #     advertiser=request.user.profile.merchant.advertiser_ptr)

        list_title = "My Deals"
        list_description = "All deals posted by you"

        # get the rendered list of deals
        rendered_deal_list = self.render_deal_list(
            request,
            queryset=deals,
            title=list_title,
            description=list_description,
            action_url='merchant_manage_deal',
            pagination_base_url=reverse('merchant_manage_deals')
        )
        context = {
            'rendered_deal_list': rendered_deal_list,
        }

        return render(request, 'merchant/deals.html', context)


class ManageDealView(MerchantMixin, View):
    """Manage a single deal"""
    def get(self, request, deal_slug):
        """Renders a page showing a deal that was created by a merchant
        """
        deal = get_object_or_404(Deal, slug=deal_slug)
        if deal.advertiser != request.user.profile.merchant.advertiser_ptr:
            messages.add_message(
                request, messages.ERROR,
                'You are not allowed to manage this deal'
            )
            return redirect(reverse('merchant_manage_deals'))
        context_data = {
            'deal': deal,
            'breadcrumbs': [
                {'name': 'Merchant', 'url': reverse('merchant_manage_deals')},
                {'name': 'Deals', }
            ]
        }
        return render(request, 'merchant/deal.html', context_data)

    def post(self, request, deal_slug):
        """Updates information about a deal that was created by a merchant.
        """

        dealform = DealForm(request.POST, request.FILES)
        deal = get_object_or_404(Deal, slug=deal_slug)
        if deal.advertiser != request.user.profile.merchant.advertiser_ptr:
            messages.add_message(
                request, messages.ERROR,
                'You are not allowed to manage this deal'
            )
            return redirect(reverse('merchant_manage_deals'))

        if dealform.is_valid():
            dealform.save(deal)
            messages.add_message(
                request, messages.SUCCESS, 'The deal was updated successfully.'
            )
        else:
            messages.add_message(
                request, messages.ERROR,
                'An error occurred while performing the operation.'
            )
        return redirect(
            reverse('merchant_manage_deal', kwargs={'deal_slug': deal.slug})
        )


class TransactionsView(MerchantMixin, View):
    """View transactions for a merchant"""
    def get(self, request):
        """Renders a page with a table showing a deal, its buyer,
        quantity bought, time of purchase, and its price
        """
        context_data = []
        return render(request, 'merchant/transactions.html', context_data)


class TransactionView(MerchantMixin, View):
    """View transactions detail for a merchant"""
    def get(self, request, transaction_id):
        """Renders a detailed view about a transaction """
        context_data = []
        return render(request, 'merchant/transactions.html', context_data)


class CreateDealView(MerchantMixin, View):
    def get(self, request):
        """Renders a form for creating deals """
        pass

    def post(self, request):
        """Creates a deal"""
        pass


class MerchantView(MerchantMixin, View):
    def get(self, request, merchant_slug):
        """Renders a view containing information about a merchant"""
        pass