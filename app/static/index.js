const fileInput = document.querySelector("#fileInput");
const browseBtn = document.querySelector("#browseBtn");

const uploadURL = `http://127.0.0.1:5000/handle_file_upload`;

browseBtn.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  
  uploadFile();
});

const uploadFile = () => {
  console.log("file added uploading");

  files = fileInput.files;
  const formData = new FormData();
  formData.append("UploadedFile", files[0]);

  //show the uploader


  // upload file
  const xhr = new XMLHttpRequest();

  // listen for upload progress
 

  xhr.open("POST", uploadURL);
  xhr.send(formData);
};