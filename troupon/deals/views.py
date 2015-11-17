from django.shortcuts import render,render_to_response,redirect
from django.views.generic import TemplateView, View
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template import Engine, RequestContext, loader
from haystack.query import SearchQuerySet
from django.core.paginator import Paginator
from django.core.context_processors import csrf
from deals.models import Category, Deal, STATE_CHOICES, EPOCH_CHOICES
from deals.baseviews import DealListBaseView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime
import cloudinary


class HomePageView(DealListBaseView):
    """ View class that handles display of the homepage.
        Overrides the base get method, but still uses the base render_deal_list method
        to get the rendered latest deals listing.
    """

    def get(self, request, *args, **kwargs):

        # get the popular categories:
        popular_categories = Category.objects.all()[:12]

        # get the featured deals:
        featured_deals = Deal.objects.filter(featured=True).order_by('pk')[:5]

        # get the latest deals i.e. sorted by latest date:
        latest_deals = Deal.objects.filter(active=True).order_by('date_last_modified')
        list_title = "Latest Deals"
        list_description = "Checkout the hottest new deals from all your favourite brands:"

        # get the rendered list of deals
        rendered_deal_list = self.render_deal_list(
            request,
            deals=latest_deals,
            title=list_title,
            description=list_description,
            pagination_base_url=reverse('deals')
        )
        context = {
            'search_options': {
                'query': "",
                'states': {'choices': STATE_CHOICES, 'default': 25},
            },
            'popular_categories': popular_categories,
            'featured_deals': featured_deals,
            'rendered_deal_list': rendered_deal_list
        }
        context.update(csrf(request))
        return render(request,'deals/index.html', context)

class DealsView(DealListBaseView):
    """ View class that handles display of the deals page.
        Simply configures the options and makes use of the base methods
        to render return latest deals listing.
    """

    deals = Deal.objects.filter(active=True).order_by('date_last_modified')
    title = "Latest Deals"
    description = "See all the hottest new deals from all your favourite brands:"


class DealView(View):
    """This handles request for each deal by id.
    """

    def get(self, *args, **kwargs):
        deal_id = self.kwargs.get('deal_id')  # get deal_id from request
        if not deal_id:
            deals = Deal.objects.all()
            engine = Engine.get_default()
            template = engine.get_template('deals/list.html')
            context = RequestContext(self.request, {'deals': deals})
            return HttpResponse(template.render(context))
        try:
            deal = Deal.objects.get(id=deal_id)
        except Deal.DoesNotExist:
            raise Http404('Deal does not exist')

        # Replace template object compiled from template code
        # with an application template.
        # Use Engine.get_template(template_name)
        engine = Engine.get_default()
        template = engine.get_template('deals/detail.html')

        # set result in RequestContext
        search_options = {
                            'query': "",
                            'states': {
                                'choices': STATE_CHOICES, 'default': 25
                                },
                        }
        context = RequestContext(
            self.request,
            {
                'deal': deal,
                'search_options': search_options
            })
        return HttpResponse(template.render(context))

    def post(self, *args, **kwargs):
        """ Upload a deal photo to cloudinary then creates deal
        """
        title = self.kwargs.get('title')
        photo = self.request.FILES.get('photo')
        self.upload(photo, title)
        return redirect(reverse('deals'))

    def upload(self, file, title):
        """ Upload deal photo to cloudinary
        """
        return cloudinary.uploader.upload(
                file,
                public_id=title
            )

class DealSearchView(View):

    ''' Haystack seach class for auto complete.'''

    template_name = 'deals/ajax_search.html'

    def post(self,request):
        deals = SearchQuerySet().autocomplete(content_auto=request.GET.get('q', ''))
        return render(request, self.template_name, {'deals': deals})


class DealSearchCityView(DealListBaseView):

    ''' class to search for city via title and states'''

    def get(self, request, *args, **kwargs):
        value = request.GET.get('q', '')
        cityquery = int(request.GET.get('city', '25'))
        # get the deal results:
        deals = Deal.objects.filter(title__icontains=value).filter(state__icontains=cityquery)

        # get the rendered list of deals
        rendered_deal_list = self.render_deal_list(
            request,
            deals=deals,
            title="Search Results",
            zero_items_message ='Your search - {} - in {} did not match any deals.'.format(value,STATE_CHOICES[cityquery-1][1]), 
            description='{} deal(s) found for this search.' .format(len(deals))
            #pagination_base_url=reverse('deals')
        )
        context = {
            'search_options': {
                'query': value,
                'states': { 'choices': STATE_CHOICES, 'default': 25 },
            },
            'rendered_deal_list': rendered_deal_list
        }
        context.update(csrf(request))
        return render(request,'deals/searchresult.html', context)


class DealSlugView(View):
    """ Respond to routes to deal url using slug
    """
    def get(self, *args, **kwargs):
        deal_slug = self.kwargs.get('deal_slug')
        try:
            deal = Deal.objects.filter(slug=deal_slug)
            if len(deal) > 1:
                deal = deal[0]
            else:
                deal = deal[0]
        except (Deal.DoesNotExist, AttributeError):
            raise Http404('Deal with this slug not found!')

        engine = Engine.get_default()
        template = engine.get_template('deals/detail.html')
        context = RequestContext(self.request, {'deal': deal})

        return HttpResponse(template.render(context))


class DealCategoryView(DealListBaseView):
    """ Respond to routes to deal categories using slug
    """
    def get(self, *args, **kwargs):
        category_slug = self.kwargs.get('category_slug')
        try:
            category = Category.objects.get(slug=category_slug)

        except Category.DoesNotExist:
            raise Http404('Category not found!')

        deals = Deal.objects.filter(category=category)
        title = "Latest Deals in {}".format(category.name)
        description = "See all the hottest new deals in {}"\
            .format(category.name)

        rendered_deal_list = self.render_deal_list(
            self.request,
            deals=deals,
            title=title,
            description=description,
        )
        context = {
            'search_options': {
                'query': "",
                'states': {'choices': STATE_CHOICES, 'default': 25},
            },
            'rendered_deal_list': rendered_deal_list
        }

        return render(self.request, 'deals/deal_list_base.html', context)


class CategoryView(View):
    """ List all categories
    """
    zero_items_message = "Sorry, no deals found!"
    num_page_items = 9
    min_orphan_items = 3
    show_page_num = 1
    pagination_base_url = ""
    categories = Category.objects.all()
    title = "Category Listing for All Available Deals"
    description = "See all categories to choose from"

    def get(self, *args, **kwargs):

        engine = Engine.get_default()
        template = engine.get_template('deals/categories.html')

        # paginate deals and get the specified page:
        paginator = Paginator(
            self.categories,
            self.num_page_items,
            self.min_orphan_items,
        )

        try:
            # get the page number if present in request.GET
            show_page_num = self.request.GET.get('pg')
            if not show_page_num:
                show_page_num = self.show_page_num
            categories_page = paginator.page(show_page_num)
        except PageNotAnInteger:
            # if page is not an integer, deliver first page.
            categories_page = paginator.page(1)
        except EmptyPage:
            # if page is out of range, deliver last page of results.
            categories_page = paginator.page(paginator.num_pages)

        # set the description to be used in the list header:
        if categories_page.paginator.count:
            description = self.description
        else:
            description = self.zero_items_message

        context = RequestContext(
                self.request,
                {'search_options': {
                    'query': "",
                    'states': {'choices': STATE_CHOICES, 'default': 25},
                },
                'categories_page': categories_page,
                'title': self.title,
                'description': description,
                'pagination_base_url': self.pagination_base_url,
                'page': True,
            })

        return HttpResponse(template.render(context))

class AboutView(View):
    '''displays about us page'''
    def get(self, *args, **kwargs):
        return render(self.request, 'deals/about.html')

class InvestorView(View):
    '''displays investor page'''
    def get(self, *args, **kwargs):
        return render(self.request, 'deals/investor.html')

class TeamView(View):
    '''displays team page'''
    def get(self, *args, **kwargs):
        return render(self.request, 'deals/team.html')

class SupportView(View):
    '''displays support page'''
    def get(self, *args, **kwargs):
        return render(self.request, 'deals/support.html')