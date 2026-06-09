import scrapy


def clean_text(value):
    if not value:
        return ""
    return " ".join(value.strip().split())


def first_text(response, selectors):
    for selector in selectors:
        value = response.css(selector).get()
        value = clean_text(value)
        if value:
            return value
    return ""


def unique_list(values):
    result = []
    for value in values:
        value = clean_text(value)
        if value and value not in result:
            result.append(value)
    return result


class CareerVietSpider(scrapy.Spider):
    name = "careerviet"

    start_urls = [
        "https://careerviet.vn/viec-lam/cntt-phan-cung-mang-cntt-phan-mem-c63,1-trang-1-vi.html"
    ]

    custom_settings = {
        "FEED_EXPORT_ENCODING": "utf-8-sig",
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def parse(self, response):
        jobs = response.css("div[class*='job-item']")

        for job in jobs:
            link = job.css(".figcaption .title h2 a::attr(href)").get()

            if link:
                yield response.follow(
                    link,
                    callback=self.parse_job
                )

        current_page = response.meta.get("page", 1)

        if current_page < 1:
            next_page = current_page + 1

            next_url = (
                "https://careerviet.vn/viec-lam/"
                f"cntt-phan-cung-mang-cntt-phan-mem-c63,1-trang-{next_page}-vi.html"
            )

            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={"page": next_page}
            )

    def parse_job(self, response):
        job_title = first_text(response, [
            ".job-desc h1.title::text",
            "div.title > h2::text",
            ".job-detail-page h1::text",
            "h1::text",
        ])

        company = first_text(response, [
            ".job-desc a::text",
            ".job-detail-page .caption > a::text",
            ".job-detail-page div.head-right a::text",
            ".company-name a::text",
            "#aboutustp-desktop-not-login .top-job-info div::text",
        ])

        job_location = first_text(response, [
            "#tab-1 div:nth-child(1) a::text",
            "#info-career-desktop li.info-workplace a::text",
            ".right-welfares a::text",
            ".detail-row.box-welfares .hide-in-mobile a::text",
        ])

        date_posted = first_text(response, [
            "#tab-1 div:nth-child(2) p::text",
            "tr:nth-child(6) > td.content > p::text",
        ])

        job_field = unique_list(
            response.css("#tab-1 div:nth-child(2) li:nth-child(2) a::text").getall()
            or response.css("#info-career-desktop li:nth-child(5) a::text").getall()
            or response.css(".job-detail-page tr:nth-child(1) a::text").getall()
            or response.css("#info-career-desktop li:nth-child(5) a::text").getall()
        )

        job_type = first_text(response, [
            "li:nth-child(3) > p::text",
            ".job-detail-page tr:nth-child(3) td.content > p::text",
        ])

        salary = first_text(response, [
            "#tab-1 div:nth-child(3) li:nth-child(1) > p::text",
            "#info-career-desktop li:nth-child(3) > div::text",
            ".job-detail-page tr:nth-child(2) td.content strong::text",
        ])

        experience = first_text(response, [
            "#tab-1 div:nth-child(3) li:nth-child(2) > p::text",
            "#info-career-desktop li:nth-child(4) > div::text",
            ".body-template div div div:nth-child(2) tr:nth-child(2) td.content > p::text",
            ".body-template div div div:nth-child(2) td.content > p::text",
            ".full-content > div:nth-child(2) p:nth-child(3)::text",
            "#jobDetailContent div:nth-child(2) > table > tbody > tr:nth-child(2) > td.content > p::text",
            ".full-content > div:nth-child(2) > div li:last-child::text",
        ])

        pos = first_text(response, [
            "#tab-1 div:nth-child(3) li:nth-child(3) > p::text",
            "#info-career-desktop li:nth-child(5) > div::text",
            ".job-detail-page tr:nth-child(4) td.content > p::text",
            "#info-career-desktop li:nth-child(2) > div::text",
        ])

        deadline = first_text(response, [
            "tr:nth-child(5) > td.content > p::text",
            "div:nth-child(3) li:nth-child(4) > p::text",
            "#info-career-desktop li:nth-child(6) > div::text",
            "#info-career-desktop li:nth-child(4) > div::text",
            "#tab-1 div:nth-child(3) li:nth-child(3) > p::text",
        ])

        yield {
            "job_title": job_title,
            "company": company,
            "job_location": job_location,
            "date_posted": date_posted,
            "job_field": ", ".join(job_field),
            "job_type": job_type,
            "salary": salary,
            "experience": experience,
            "pos": pos,
            "deadline": deadline,
            "job_url": response.url,
        }