import scrapy


def clean_text(value):
    """Xóa khoảng trắng thừa và xuống dòng trong chuỗi."""
    if not value:
        return ""
    return " ".join(value.strip().split())


def first_text(response, selectors):
    """Lấy giá trị đầu tiên không rỗng từ danh sách các selector."""
    for selector in selectors:
        value = response.css(selector).get()
        value = clean_text(value)
        if value:
            return value
    return ""


def unique_list(values):
    """Lấy danh sách các giá trị duy nhất từ danh sách đầu vào."""
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

    def parse(self, response):
        # Lấy tất cả các phần tử chứa thông tin công việc
        jobs = response.css("div[class*='job-item']") 

        # Duyệt qua từng phần tử công việc và lấy liên kết chi tiết
        for job in jobs:
            link = job.css(".figcaption .title h2 a::attr(href)").get()

            if link:
                # Nếu link là đường dẫn tương đối, chuyển nó thành đường dẫn tuyệt đối
                yield response.follow(
                    link,
                    callback=self.parse_job
                )

        # Lấy số trang hiện tại từ meta, nếu không có thì mặc định là 1
        current_page = response.meta.get("page", 1)
        print(f"Crawling page {current_page}...")
        # Giới hạn số trang cần crawl
        if current_page < 5:
            next_page = current_page + 1

            # Tạo URL cho trang tiếp theo dựa trên mẫu URL của trang hiện tại
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

        job_id = response.url.split(".")[-2]

        job_title = first_text(response, [
            "div[class*='job'] h1::text",
            "div[class*='job'] h2::text",
        ])

        company = first_text(response, [
            "div[class*='job'] a[class*='company']::text",
            ".tit_company::text",
            "div[class*='company'] h2::text",
        ])

        job_location = first_text(response, [
            ".place::text",
            "p.list-workplace a::text",
            ".map a::text",
        ])

        date_posted = first_text(response, [
            ".template-202-wrap .content tr:last-child .content p::text",
            ".template02 .content  tr:nth-child(4) .content p::text",
            ".template .content  tr:nth-last-child(2) .content p::text",
            ".item-blue:nth-child(2) li:nth-child(1) p::text",
            ".table tr:nth-child(8) td.content p::text",
            ".table div:nth-child(1) tr:nth-child(3) td.content p::text",
        ])

        job_field = unique_list(
            response.css(".item-blue:nth-child(2) li:nth-child(2) p a::text").getall()
            or response.css("div[class*='template'] .content tr:nth-child(1) .content a::text").getall()
            or response.css(".info-career li:nth-child(5) a::text").getall()
            or response.css("#info-career-mb li:nth-child(3) a::text").getall()
        )



        job_type = first_text(response, [
            ".item-blue:nth-child(2) li:nth-child(3) p::text",
            ".template .content  tr:nth-child(3) .content p::text",
            "div[class*='template-'] .content tr:nth-child(3) td.content p::text",
        ])

        salary = first_text(response, [
            ".item-blue:nth-child(3) li:nth-child(1) > p::text",
            "div[class*='template-'] .content .green strong::text",
            "div[class*='template'] .content .green strong::text",
            ".info-career li:nth-child(3) div::text",
            "#info-career-mb li:nth-child(6) span::text",
        ])

        count_list = response.css(".item-blue:nth-child(3) li p::text").getall()
        if len(count_list) > 3:
            experience = response.css(".item-blue:nth-child(3) li:nth-child(2) p::text").get()
        else:
            experience = first_text(response, [
                ".template-16 .detail-row:nth-child(5) li:nth-child(2)::text",
                ".template .content tr:nth-child(5) .content p::text",
                "section.job-detail-content > div:nth-child(4) li:nth-child(2)::text",
                ".template02 .detail-row:nth-child(2) p:nth-child(6)::text"
                ".template-202-wrap .content tr:nth-child(6) .content p::text",
                ".template-205-wrap .content div:nth-child(2) tr:nth-child(3) .content p::text",
                ".template-201 .detail-row:nth-child(3) li:nth-child(3)::text",
                ".template-200 .detail-row:nth-child(3) li:nth-child(2)::text",
                ".template-200 .detail-row:nth-child(3) p:nth-child(2)::text",
            ])

        pos = first_text(response, [
            ".template02 .content  tr:nth-child(5) .content p::text",
            ".template .content  tr:nth-child(4) .content p::text",
            ".item-blue:nth-child(3) li:nth-last-child(2)  > p::text",
            ".template-205-wrap .content div:nth-child(2) tr:nth-child(2) .content p::text",
            ".template-202-wrap .content tr:nth-child(5) .content p::text",
            ".info-career li:nth-child(2) div::text",
            "#info-career-mb li:nth-child(2) span::text",
        ])

        deadline = first_text(response, [
            "div[class*='template'] .content .red::text",
            ".item-blue:nth-child(3) li:last-child > p::text",
            ".info-career li:nth-child(4) div::text",
            "#info-career-mb li:nth-child(7) span::text",
        ])
    
        yield {
            "job_id": job_id,
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