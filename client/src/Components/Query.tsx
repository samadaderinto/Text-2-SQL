import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Header } from "../layouts/Header";
import ReactPaginate from "react-paginate";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import SideBar from "../layouts/SideBar";
import { FiSearch } from 'react-icons/fi';
import { MdOutlineDownload } from "react-icons/md";
import { ClipLoader } from 'react-spinners';


const Query = () => {
  const location = useLocation();
  const data = location.state?.data || []; // Access the passed data

  const itemsPerPage = 5;
  const [currentPage, setCurrentPage] = useState(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const totalPages = Math.ceil(data.length / itemsPerPage);
  const offset = currentPage * itemsPerPage;
  const currentItems = data.slice(offset, offset + itemsPerPage);

  useEffect(() => {
    if (data.length > 0) {
      setLoading(false);
    }
  }, [data]);

  const handlePageClick = ({ selected }: { selected: number }) => {
    setCurrentPage(selected);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const filteredItems = currentItems.filter((item: { name: string; }) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <Header />
      <SideBar />
      <div className="Query_Container">
        <section className="Query_Header">
          <h1>Items</h1>
          <button className="Query_Download_Btn">
            Download <MdOutlineDownload style={{ fontSize: '24px' }} />
          </button>
        </section>

        <section className="Query_Body">
          <div className="Input_Holder">
            <FiSearch style={{ cursor: 'pointer' }} />
            <input
              type="text"
              placeholder="Search Name"
              value={searchTerm}
              onChange={handleSearch}
            />
          </div>

          <div className="Query_Form_Header">
            <span className="Query_Name">
              <p>Product Name</p>
            </span>
            <ul>
              <li>Category</li>
              <li>Status</li>
              <li>Price</li>
              <li>Sold</li>
              <li>Sales</li>
              <li>Action</li>
            </ul>
          </div>

          {loading ? (
            <div className="spinner-container">
              <ClipLoader color={"#123abc"} loading={loading} size={50} />
            </div>
          ) : (
            <>
              <section className="Query_Item_container">
                {filteredItems.length > 0 ? (
                  filteredItems.map((item: any, index: number) => (
                    <div key={index}>
                      <p>{item.name}</p>
                      <p>{item.category}</p>
                      <p>{item.status}</p>
                      <p>{item.price}</p>
                      <p>{item.sold}</p>
                      <p>{item.sales}</p>
                      <button>Action</button>
                    </div>
                  ))
                ) : (
                  <p style={{ marginLeft: '-45%' }}>No items available</p>
                )}
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
            </>
          )}
        </section>
      </div>
    </>
  );
};

export default Query;
