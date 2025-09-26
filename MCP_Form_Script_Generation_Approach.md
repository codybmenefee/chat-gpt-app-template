# **MCP Form Script Generation Approach**

## **Overview**

The MCP (Model Context Protocol) approach enables automated generation of form filling scripts that integrate seamlessly with the existing `form_fillers/` and `form_fillers_core/` framework. The system uses AI agents to analyze PDFs, trace data sources, and generate production-ready TypeScript scripts following established patterns.

## **Core Architecture**

### **Input Requirements**
- **PDF File**: Tagged PDF with meaningful field names (e.g., `"client_first_name"`)
- **Workflow Context**: `workflowCompletionId`, `formCompletionId`, `objectId`
- **Client Type**: `cst`, `aviso`, `addenda`, `pwl` (determines utility patterns)

### **Output Deliverables**
1. **Main Form Script**: `{client}_{form_name}.ts` - Production-ready form filler
2. **Utility Enhancements**: `{client}_utils_enhancements.ts` - Suggested utility improvements
3. **Schema Extensions**: `fetch_ov_data_extensions.ts` - New GraphQL queries if needed
4. **Documentation**: `{form_name}_mapping_guide.md` - Mapping rationale and usage

## **MCP Tools Specification**

### **Phase 1: PDF Analysis Tools**

#### **`analyze_pdf_fields_windmill`**
```typescript
interface AnalyzePdfFieldsInput {
  s3Bucket: string;
  s3Key: string;
}

interface AnalyzePdfFieldsOutput {
  fields: Array<{
    name: string;
    type: 'text' | 'checkbox' | 'dropdown' | 'radio';
    options?: string[];
  }>;
  fieldMapTemplate: string; // Ready-to-use FIELD_MAP object
  signatureFields: Array<{
    name: string;
    page: number;
    coordinates: { x: number; y: number; width: number; height: number };
  }>;
}
```

#### **`generate_windmill_field_map`**
```typescript
interface GenerateFieldMapInput {
  fields: Array<FieldInfo>;
  clientType: 'cst' | 'aviso' | 'addenda' | 'pwl';
}

interface GenerateFieldMapOutput {
  fieldMapObject: string; // Complete FIELD_MAP TypeScript object
  unmappedFields: string[];
  suggestedMappings: Record<string, string>;
}
```

### **Phase 2: Data Source Analysis Tools**

#### **`analyze_workflow_for_form_filling`**
```typescript
interface AnalyzeWorkflowInput {
  workflowCompletionId: string;
  formCompletionId: string;
  objectId: string;
}

interface AnalyzeWorkflowOutput {
  userData: UserDocument;
  accountData: AccountDocument;
  currentDate: string;
  customFields: Array<{ key: string; value: any }>;
  availableDataSources: {
    user: boolean;
    account: boolean;
    subAccounts: boolean;
    affiliations: boolean;
    bankAccounts: boolean;
  };
}
```

#### **`suggest_client_specific_mapping`**
```typescript
interface SuggestMappingInput {
  fieldName: string;
  fieldType: string;
  availableData: any;
  clientType: string;
  context: string;
}

interface SuggestMappingOutput {
  suggestedMapping: string;
  clientUtility: string;
  confidence: number;
  reasoning: string;
  alternatives: Array<{
    mapping: string;
    confidence: number;
    reasoning: string;
  }>;
}
```

### **Phase 3: Code Generation Tools**

#### **`generate_form_filler_script`**
```typescript
interface GenerateScriptInput {
  fieldMappings: Record<string, string>;
  clientType: string;
  formMetadata: {
    fileName: string;
    s3Key: string;
    description: string;
  };
  dataSources: any;
}

interface GenerateScriptOutput {
  scriptContent: string;
  imports: string[];
  dependencies: string[];
  validationResults: {
    syntaxValid: boolean;
    followsPatterns: boolean;
    missingImports: string[];
  };
}
```

### **Phase 4: Validation & Testing Tools**

#### **`validate_form_script`**
```typescript
interface ValidateScriptInput {
  scriptContent: string;
  clientType: string;
  referenceScripts: string[];
}

interface ValidateScriptOutput {
  isValid: boolean;
  followsPatterns: boolean;
  missingImports: string[];
  missingDataMappings: string[];
  suggestions: string[];
  patternCompliance: {
    importStructure: boolean;
    functionSignature: boolean;
    s3Configuration: boolean;
    dataInitialization: boolean;
    errorHandling: boolean;
  };
}
```

#### **`test_form_generation_windmill`**
```typescript
interface TestFormInput {
  scriptContent: string;
  workflowCompletionId: string;
  formCompletionId: string;
  objectId: string;
}

interface TestFormOutput {
  success: boolean;
  filledFormPath: string;
  errors: string[];
  executionLog: string;
  fieldMappingResults: Record<string, any>;
}
```

---

# **Implementation Plan**

## **Phase 1: Foundation Tools (Weeks 1-2)**

### **1.1 PDF Analysis Tools**
- [ ] **Build `analyze_pdf_fields_windmill`**
  - Integrate with existing `field_map_generator.ts` logic
  - Extract field types and options
  - Generate signature field coordinates
- [ ] **Build `generate_windmill_field_map`**
  - Create FIELD_MAP object structure
  - Identify unmapped fields
  - Generate initial mapping suggestions

### **1.2 Validation Framework**
- [ ] **Create script comparison utilities**
  - Parse existing client scripts
  - Extract patterns and conventions
  - Build compliance checking

### **1.3 Test Data Preparation**
- [ ] **Collect test PDFs and scripts**
  - Use existing client PDFs
  - Extract reference field mappings
  - Create test dataset

## **Phase 2: Data Analysis Tools (Weeks 3-4)**

### **2.1 Workflow Analysis**
- [ ] **Build `analyze_workflow_for_form_filling`**
  - Integrate with existing `fetch_ov_data.ts`
  - Extract available data sources
  - Identify custom fields

### **2.2 Mapping Intelligence**
- [ ] **Build `suggest_client_specific_mapping`**
  - Analyze field names for context
  - Map to existing utility functions
  - Generate confidence scores

### **2.3 Validation Against Existing Scripts**
- [ ] **Test with CST forms**
  - Compare generated mappings to `01_en_spark_2_0_education_savings_plan_application_form_pdf.ts`
  - Validate field mapping accuracy
  - Refine mapping logic

## **Phase 3: Code Generation (Weeks 5-6)**

### **3.1 Script Generation**
- [ ] **Build `generate_form_filler_script`**
  - Follow exact framework patterns
  - Generate proper imports and structure
  - Include error handling

### **3.2 Client-Specific Patterns**
- [ ] **Implement client utility integration**
  - CST: `getCustomFieldValue`, `formatAddress`
  - Aviso: Custom field patterns, address formatting
  - Addenda: `centsToDollar`, `calculateNetworth`
  - PWL: Complex mapping patterns

### **3.3 Validation Testing**
- [ ] **Test with Aviso forms**
  - Compare to `en_av_02_new_account_application_form_pdf.ts`
  - Validate complex field mappings
  - Test joint account handling

## **Phase 4: Advanced Features (Weeks 7-8)**

### **4.1 Advanced Validation**
- [ ] **Build `validate_form_script`**
  - Pattern compliance checking
  - Import validation
  - Data mapping verification

### **4.2 Testing Framework**
- [ ] **Build `test_form_generation_windmill`**
  - Execute generated scripts
  - Compare output PDFs
  - Generate execution reports

### **4.3 Enhancement Suggestions**
- [ ] **Build utility enhancement tools**
  - Analyze common patterns
  - Suggest utility improvements
  - Generate enhancement proposals

## **Phase 5: Integration & Refinement (Weeks 9-10)**

### **5.1 End-to-End Testing**
- [ ] **Test with Addenda forms**
  - Complex custom field mappings
  - Multiple data sources
  - Advanced transformations

### **5.2 PWL Integration**
- [ ] **Test with PWL forms**
  - Complex mapping patterns
  - Multiple client scenarios
  - Advanced validation

### **5.3 Production Readiness**
- [ ] **Performance optimization**
- [ ] **Error handling refinement**
- [ ] **Documentation completion**

---

# **Validation Strategy**

## **Test Cases**

### **CST Forms (Simple)**
- **PDF**: `01.EN_Spark 2.0 ESP Form - 2.1.pdf`
- **Reference**: `01_en_spark_2_0_education_savings_plan_application_form_pdf.ts`
- **Focus**: Basic field mapping, custom fields, date formatting

### **Aviso Forms (Complex)**
- **PDF**: `EN_AV_02_New account application form.pdf`
- **Reference**: `en_av_02_new_account_application_form_pdf.ts`
- **Focus**: Joint accounts, complex mappings, custom field patterns

### **Addenda Forms (Advanced)**
- **PDF**: Various addenda forms
- **Reference**: Multiple addenda scripts
- **Focus**: Utility functions, complex transformations

### **PWL Forms (Expert)**
- **PDF**: `EN_PWL_2025_NCAF - Individual.pdf`
- **Reference**: `EN_PWL_2025_NCAF_Individual_pdf.ts`
- **Focus**: Complex mapping patterns, multiple data sources

## **Success Metrics**

### **Accuracy Metrics**
- **Field Mapping Accuracy**: >95% correct field mappings
- **Pattern Compliance**: 100% adherence to framework patterns
- **Data Source Accuracy**: >90% correct data source identification

### **Quality Metrics**
- **Generated Script Quality**: Indistinguishable from manual scripts
- **Error Rate**: <5% execution errors
- **Performance**: Scripts execute within 30 seconds

### **Validation Process**
1. **Generate script** using MCP tools
2. **Compare field mappings** to reference script
3. **Execute both scripts** with same test data
4. **Compare output PDFs** for visual accuracy
5. **Validate data accuracy** field by field
6. **Refine tools** based on discrepancies

## **Iterative Refinement**

### **Weekly Validation Cycles**
- **Week 1**: PDF analysis accuracy
- **Week 2**: Data source identification
- **Week 3**: Field mapping accuracy
- **Week 4**: Code generation quality
- **Week 5**: End-to-end validation
- **Week 6**: Performance optimization
- **Week 7**: Advanced feature testing
- **Week 8**: Production readiness
- **Week 9**: Integration testing
- **Week 10**: Final validation

## **Key Success Factors**

1. **Framework-Specific Design**: Every tool is tailored to work within the existing `form_fillers/` and `form_fillers_core/` architecture

2. **Phased Implementation**: 10-week plan with clear milestones and validation points

3. **Real-World Testing**: Using existing client scripts as reference points for validation

4. **Iterative Refinement**: Weekly validation cycles to continuously improve accuracy

5. **Production-Ready Output**: Generated scripts that are indistinguishable from manually created ones

## **Next Steps**

1. **Start with Phase 1**: Build the PDF analysis tools first
2. **Use existing scripts as test cases**: Compare generated output to reference implementations
3. **Iterate quickly**: Weekly validation cycles to catch issues early
4. **Focus on accuracy**: Ensure field mappings are correct before moving to advanced features

The plan is designed to be manageable and focused, with clear validation points to ensure we don't get lost in scope while building a robust, production-ready system.
