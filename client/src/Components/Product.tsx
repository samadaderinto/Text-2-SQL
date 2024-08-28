import { useReducer, useEffect, Key } from 'react';
import { IoIosAddCircleOutline } from 'react-icons/io';
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from 'react-icons/md';
import { FiSearch } from 'react-icons/fi';
import { Header } from '../layouts/Header';
import Sidebar from '../layouts/SideBar';
import { useNavigate } from 'react-router-dom';
import ReactPaginate from 'react-paginate';
import api from '../utils/api';

const initialState = {
  currentPage: 0,
  input: '',
  data: [],
  totalPages: 0,
};

function reducer(state: any, action: { type: any; payload: any; }) {
  switch (action.type) {
    case 'SET_CURRENT_PAGE':
      return { ...state, currentPage: action.payload };
    case 'SET_INPUT':
      return { ...state, input: action.payload };
    case 'SET_DATA':
      return { ...state, data: action.payload };
    case 'SET_TOTAL_PAGES':
      return { ...state, totalPages: action.payload };
    default:
      return state;
  }
}

export const Product = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { currentPage, input, data, totalPages } = state;
  const itemsPerPage = 15;
  const offset = currentPage * itemsPerPage;
  
  const nav = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(
          `/product/search/?offset=${currentPage * itemsPerPage}&limit=${itemsPerPage}&query=${input}`,
        );
        const totalItems = response.data.totalCount || 0;
        dispatch({ type: 'SET_DATA', payload: response.data.items || [] });
        dispatch({ type: 'SET_TOTAL_PAGES', payload: Math.ceil(totalItems / itemsPerPage) });
      } catch (error) {
        console.error("Error fetching data", error);
        dispatch({ type: 'SET_TOTAL_PAGES', payload: 1 });  // Fallback to 1 page in case of an error
      }
    };

    fetchData();
  }, [currentPage, input]);


  const handlePageClick = (event: { selected: any; }) => {
    dispatch({ type: 'SET_CURRENT_PAGE', payload: event.selected });
  };

  return (
    <div className="Product_Container">
      <Header />
      <Sidebar />
      <section className="Add_Product">
        <h1>All Products</h1>
        <span onClick={() => nav('/product/add')}>
          <IoIosAddCircleOutline className="Product_Icon" />
          Add new Product
        </span>
      </section>
      <section className="Product_Table_Section">
        <div>
          <span>
            <FiSearch className="Search_Icon" />
            <input
              type="text"
              value={input}
              onChange={(e) => dispatch({ type: 'SET_INPUT', payload: e.target.value })}
              placeholder="Search Name"
            />
          </span>
          <MdOutlineCalendarToday />
        </div>
        <div className="Product_Table_list_header">
          <span>
            <input type="checkbox" />
            <p>Product Name</p>
          </span>
          <ul>
            <li>Category</li>
            <li>Status</li>
            <li>Price</li>
            <li>Sold</li>
            <li>Sales</li>
          </ul>
          <p>Action</p>
        </div>
        <div className="Product_Table_List_content">
          {data.map((item: { imageUrl: any; name: any; category: any; status: any; price: any; sold: any; sales: any; }, index: Key | null | undefined) => (
            <nav key={index}>
              <span>
                <input type="checkbox" />
                <article className="Product_Img_Container">
                  <img src={item.imageUrl || ''} alt={item.name || 'Product Image'} />
                </article>
                <p>{item.name || 'Product Name'}</p>
              </span>
              <span className="Product_Details">
                <p className="Product_Category">{item.category || 'Category'}</p>
                <p className="Product_Available">{item.status || 'Status'}</p>
                <p>${item.price || '0.00'}</p>
                <p>{item.sold || '0'}</p>
                <p>${item.sales || '0.00'}</p>
              </span>
              <p className="Product_Icons">
                <MdOutlineEdit />
                <MdOutlineDelete />
              </p>
            </nav>
          ))}

          <ReactPaginate
            previousLabel={'<'}
            nextLabel={'>'}
            breakLabel={'...'}
            pageCount={totalPages}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            onPageChange={handlePageClick}
            containerClassName={'Product_pagination'}
            activeClassName={'Product_page_active'}
          />
        </div>
      </section>
    </div>
  );
};
