# Rebuild in Power BI Desktop

A Power BI Desktop report (.pbix) is currently unavailable. This folder provides a build recipe tied to the published data and notebook results.

1. Download the repository or clone it. In Power BI Desktop, use **Get Data → Text/CSV** to load `data/processed/restaurant_order_analysis_cleaned.csv`. Name the table `Restaurant Sales`.
2. In Power Query, set `date` to Date, `order_id` and `hour` to Whole Number, and `revenue` to Fixed Decimal Number. Set `month_number` and `day_number` to Whole Number. Sort `month` by `month_number` and `day_name` by `day_number`.
3. Add each measure in [measures.dax](measures.dax) separately. Format sales and sales per order as USD. Use the measures for the four headline cards.
4. Add Month and Cuisine slicers using `month` and `category`. Use Sales for the monthly, cuisine, hourly, weekday and item charts. Sort the item chart by Sales descending and apply an eight-item top filter.
5. For a separate quarter-level basket summary, import `basket_analysis_item_pairs.csv`. Its counts are already aggregated for the full quarter. Keep the Month and Cuisine slicers off that visual unless you implement pair calculation from the same filtered order lines.
6. Verify the full-period cards show $159,217.90 in sales, 5,343 orders, 12,097 items, and $29.80 sales per matched order. Then save as `Restaurant Sales and Menu Performance.pbix`.

The 137 lines without matched menu items are present in the raw CSV and excluded from the processed fact table. See the [project methodology](../README.md).
