import { useState } from 'react';
import { Header } from "../layouts/Header";
import ReactPaginate from "react-paginate";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";

const Query = () => {
  // Mock data for example purposes; replace with actual data.
  const items: any = [];
  const itemsPerPage = 5;

  const [currentPage, setCurrentPage] = useState(0);

  const totalPages = Math.ceil(items.length / itemsPerPage);
  const offset = currentPage * itemsPerPage;
  const currentItems = items.slice(offset, offset + itemsPerPage);

  const handlePageClick = ({ selected }: { selected: number }) => {
    setCurrentPage(selected);
  };

  return (
    <>
      <Header />
      <div className="Query_Container">
        <section className="Query_Header">
          <h1>Query Request Items</h1>
          <button className="Query_Download_Btn">Download</button>
        </section>
        <section className="Query_Item_container">
          {currentItems.map((item: any, index: number) => (
            <div key={index}>{item}</div>
          ))}
        </section>
        {totalPages > 1 && (
          <ReactPaginate
            previousLabel={<FaAngleLeft className="order_arrow" />}
            nextLabel={<FaAngleRight className="order_arrow" />}
            breakLabel={'...'}
            pageCount={totalPages}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            onPageChange={handlePageClick}
            containerClassName={'Product_pagination'}
            activeClassName={'Product_page_active'}
            previousClassName={'pagination_arrow'}
            nextClassName={'pagination_arrow'}
            disabledClassName={'pagination_disabled'}
          />
        )}
      </div>
    </>
  );
};

export default Query;
