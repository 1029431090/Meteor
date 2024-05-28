<script>  
import axios from 'axios';  
import MapPage from './MapPage.vue'; // 假设MapPage是另一个Vue组件  
  
export default {  
  components: {  
    MapPage, // 注册MapPage组件  
  },  
  data() {  
    return {  
      dataRange: '', // 日期范围  
      searchValue: '', // 目标筛选值  
      targetValue: '', // 提交的目标值  
      targetList: [], // 文件列表  
      tableData: [], // 表格数据  
      // 其他可能的数据...  
    };  
  },  
  methods: {  
    // 假设有一个方法来处理查询按钮的点击  
    async fetchData() {  
      try {  
        // 根据dataRange和searchValue构建查询参数  
        const params = {  
          startDate: this.dataRange[0], // 假设dataRange是包含两个日期的数组  
          endDate: this.dataRange[1],  
          search: this.searchValue,  
        };  
  
        // 发送GET请求到后端API接口  
        const response = await axios.get('http://localhost:8000/api/data', { params });  
          
        // 假设后端返回两个数组：targetList和tableData  
        this.targetList = response.data.targetList;  
        this.tableData = response.data.tableData;  
  
        // 在这里，你可能还想更新图表或其他组件的数据  
      } catch (error) {  
        console.error('Error fetching data:', error);  
        // 显示错误给用户或处理错误情况  
      }  
    },  
    // 提交目标的方法  
    async submitTarget() {  
      try {  
        // 根据targetValue发送POST请求到后端API接口  
        const response = await axios.post('http://localhost:8000/api/target', {  
          target: this.targetValue,  
          // 其他可能需要的参数...  
        });  
  
        // 处理响应，例如显示成功消息或更新UI  
        // 注意：这里可能不需要更新targetList或tableData，因为只是提交了目标  
      } catch (error) {  
        console.error('Error submitting target:', error);  
        // 显示错误给用户或处理错误情况  
      }  
    },  
    // 其他可能的方法...  
  },  
  mounted() {  
    // 如果需要，在组件加载时调用某个方法（例如fetchData）  
  },  
  // 其他选项，如computed属性、watch等...  
};  
</script>
