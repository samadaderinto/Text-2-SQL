import { useState } from "react";
import { LuImagePlus } from "react-icons/lu";
import { Header } from "../layouts/Header";
import SideBar from "../layouts/SideBar";
import axios from "axios";

export const Newcustomer = () => {
  const [formState, setFormState] = useState({
    img: null as string | null,
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    date: '',
    quantity: '',
    errors: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      date: '',
      quantity: '',
    }
  });

  const validateForm = () => {
    const newErrors = {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      date: '',
      quantity: '',
    };
    let valid = true;

    if (!formState.firstName) {
      newErrors.firstName = 'First name is required';
      valid = false;
    }
    if (!formState.lastName) {
      newErrors.lastName = 'Last Name is required';
      valid = false;
    }
    if (!formState.email) {
      newErrors.email = 'Email address is required';
      valid = false;
    }
    if (!formState.phone) {
      newErrors.phone = 'Phone number is required';
      valid = false;
    }
    if (!formState.date) {
      newErrors.date = 'Date is required';
      valid = false;
    }
    if (!formState.quantity || isNaN(Number(formState.quantity))) {
      newErrors.quantity = 'Valid quantity is required';
      valid = false;
    }
    setFormState({ ...formState, errors: newErrors });
    return valid;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormState({
      ...formState,
      [e.target.name]: e.target.value,
      errors: {
        ...formState.errors,
        [e.target.name]: '',
      }
    });
  };

  const Upload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const url = URL.createObjectURL(e.target.files[0]);
      setFormState({ ...formState, img: url });
    }
  };

  const handleCreateCustomer = async () => {
    if (validateForm()) {
      const formData = new FormData();
      formData.append('firstName', formState.firstName);
      formData.append('lastName', formState.lastName);
      formData.append('email', formState.email);
      formData.append('phone', formState.phone);
      formData.append('date', formState.date);
      formData.append('quantity', formState.quantity);

      if (formState.img) {
        const imageFile = await fetch(formState.img).then(r => r.blob());
        formData.append('image', imageFile);
      }

      try {
        await axios.post(`/customers/create/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log('Customer created successfully');
      } catch (error) {
        console.error('Error creating customer:', error);
      }
    }
  };

  return (
    <>
      <Header />
      <SideBar />
      <div className="Newcustomer_Container">
        <h1>Create New Customer</h1>
        <section className="Product_Form_Container">
          <div className="GenProduct_Container">
            <h3>Customer Information</h3>
            <form>
              <label htmlFor="First_Name">First Name</label>
              <input type="text" name="firstName" placeholder="Input customer first name" id="First_Name" value={formState.firstName} onChange={handleChange} />

              <label htmlFor="Last_Name">Last Name</label>
              <input type="text" name="lastName" id="Last_Name" placeholder="Input customer last name" value={formState.lastName} onChange={handleChange} />

              <label htmlFor="customer_Email">Email</label>
              <input type="email" name="email" id="customer_Email" placeholder="Input customer email" value={formState.email} onChange={handleChange} />

              <label htmlFor="customer_phone">Phone</label>
              <input type="tel" name="phone" id="customer_phone" placeholder="Input customer phone number" value={formState.phone} onChange={handleChange} />

              <div>
                <span className="Cancel_Btn">Cancel</span>
                <span onClick={handleCreateCustomer} className="Add_Btn">Add Customer</span>
              </div>
            </form>
          </div>
          <div className="Product_Media_Container">
            <h3>Customer Image</h3>
            <label htmlFor="fileInput">
              <section>
                {formState.img === null ? (
                  <>
                    <input type="file" onChange={Upload} style={{ display: "none" }} id="fileInput" />
                    <LuImagePlus />
                    <p>Click or drag image</p>
                  </>
                ) : (
                  <img src={formState.img} alt="Customer" />
                )}
              </section>
            </label>

            <span>
              <label htmlFor="date">Date Added</label>
              <input type="date" name="date" value={formState.date} onChange={handleChange} />

              <label htmlFor="quantity">Quantity</label>
              <input name="quantity" value={formState.quantity} onChange={handleChange} type="number" placeholder="Enter quantity" />
            </span>
          </div>
        </section>
      </div>
    </>
  )
}
