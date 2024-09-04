import { useState, ChangeEvent, useEffect } from "react";
import { LuImagePlus } from "react-icons/lu";
import SideBar from "../layouts/SideBar";
import { Header } from "../layouts/Header";
import { ProductFormStateProps } from "../types/add-product-state";
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import api from "../utils/api";
import { useNavigate } from "react-router-dom";



export const NewProduct = () => {
  const [formState, setFormState] = useState<ProductFormStateProps>({
    img: null,
    productName: '',
    productDescription: '',
    productPrice: '',
    currency: '$',
    category: '',
    quantity: '',
    store: 0,
    errors: {
      productName: '',
      productDescription: '',
      productPrice: '',
      quantity: '',
    },
  });

  const nav = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/settings/store/get/")
        setFormState({
          ...formState,
          store: response.data.user
        })

      } catch (error) {
        console.log(error)
      }
    }

    fetchData();

  }, [])

  const validateForm = (): boolean => {
    const newErrors: ProductFormStateProps['errors'] = {
      productName: '',
      productDescription: '',
      productPrice: '',
      quantity: '',
    };
    let valid = true;

    if (!formState.productName) {
      newErrors.productName = 'Product name is required';
      valid = false;
    }
    if (!formState.productDescription) {
      newErrors.productDescription = 'Product description is required';
      valid = false;
    }
    if (!formState.productPrice || isNaN(Number(formState.productPrice)) || Number(formState.productPrice) <= 0) {
      newErrors.productPrice = 'Valid product price is required';
      valid = false;
    }
    if (!formState.quantity || isNaN(Number(formState.quantity)) || Number(formState.quantity) <= 0) {
      newErrors.quantity = 'Valid product quantity is required';
      valid = false;
    }

    setFormState({ ...formState, errors: newErrors });
    return valid;
  };

  const Upload = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setFormState({ ...formState, img: file });
    }
  };

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormState({
      ...formState,
      [e.target.name]: e.target.value,
      errors: {
        ...formState.errors,
        [e.target.name]: '',
      }
    });
  };

  const handleCreateProduct = async () => {
    if (validateForm()) {
      const formData = new FormData();
      formData.append('store', formState.store?.toString() || '');
      formData.append('title', formState.productName);
      formData.append('description', formState.productDescription);
      formData.append('price', formState.productPrice);
      formData.append('currency', formState.currency);
      formData.append('category', formState.category);
      formData.append('available', formState.quantity);

      if (formState.img) {
        formData.append('image', formState.img);
      }

      try {
        await api.post(`/product/create/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        toast.success('Product created successfully!');
        nav("/product")
      } catch (error) {
        console.error('Error creating product:', error);
        toast.error('Failed to create product. Please try again.');
      }
    } else {
      toast.error('Please fill in all required fields correctly.');
    }
  };

  return (
    <div className="Newproduct_Container">
      <Header />
      <SideBar />
      <h1>Create New Product</h1>
      <section className="Product_Form_Container">
        <div className="GenProduct_Container">
          <h3>General Product Information</h3>
          <form>
            <label htmlFor="Product_Name">Product Name </label>
            <input
              type="text"
              placeholder="Input product name"
              id="Product_Name"
              name="productName"
              value={formState.productName}
              onChange={handleChange}
            />
            {formState.errors.productName && <div className="error">{formState.errors.productName}</div>}

            <label htmlFor="Product_Description">Product Description</label>
            <textarea
              name="productDescription"
              placeholder="Describe the product"
              id="Product_Description"
              value={formState.productDescription}
              onChange={handleChange}
            />
            {formState.errors.productDescription && <div className="error">{formState.errors.productDescription}</div>}

            <span>
              <article className="Select_Article">
                <label htmlFor="currency">Currency</label>
                <select
                  name="currency"
                  id="currency"
                  value={formState.currency}
                  onChange={handleChange}
                >
                  <option value="$">$</option>
                  <option value="£">£</option>
                  <option value="€">€</option>
                </select>
              </article>
              <article className="Price_Article">
                <label htmlFor="product_price">Product Price</label>
                <input
                  type="text"
                  id="product_price"
                  name="productPrice"
                  placeholder="Input price"
                  value={formState.productPrice}
                  onChange={handleChange}
                />
                {formState.errors.productPrice && <div className="error">{formState.errors.productPrice}</div>}
              </article>
            </span>
            <div>
              <span className="Cancel_Btn" onClick={()=>nav("/product")}>Cancel</span>
              <span className="Add_Btn" onClick={handleCreateProduct}>Add Product</span>
            </div>
          </form>
        </div>
        <div className="Product_Media_Container">
          <h3>Product Media</h3>
          <section>
            {formState.img === null ? (
              <>
                <label htmlFor="fileInput">
                  <input
                    type="file"
                    onChange={Upload}
                    style={{ display: "none" }}
                    id="fileInput"
                  />
                  <LuImagePlus />
                  <p>Click or drag image</p>
                </label>
              </>
            ) : (
              <img src={URL.createObjectURL(formState.img)} alt="Product" />
            )}
          </section>
          <span>
            <label htmlFor="Category">Product Category</label>
            <select
              name="category"
              id="Category"
              value={formState.category}
              onChange={handleChange}
            >
              <option value="" disabled>Select product category</option>
              <option value="fishing">fishing</option>
              <option value="sports">sports</option>
              <option value="electronics">electronics</option>
              <option value="phones">phones</option>
              <option value="pets">pets</option>
              <option value="games">games</option>
              <option value="toys">toys</option>
              <option value="tablets">tablets</option>
              <option value="computing">computing</option>
              <option value="lingerie">lingerie</option>
              <option value="books">books</option>
            </select>

            <label htmlFor="quantity">Product Quantity</label>
            <input
              type="text"
              placeholder="Input Product Quantity"
              name="quantity"
              value={formState.quantity}
              onChange={handleChange}
            />
            {formState.errors.quantity && <div className="error">{formState.errors.quantity}</div>}
          </span>
        </div>
      </section>
    </div>
  );
};


